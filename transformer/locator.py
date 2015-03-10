"""
Locate face points
"""

import cv2
import numpy as np
import subprocess

def boundary_points(points):
  """ Produce additional boundary points

  :param points: _m_ x 2 array of x,y points
  :returns: 2 additional points at the top corners
  """
  x, y, w, h = cv2.boundingRect(np.array([points], np.int32))
  buffer_percent = 0.1
  spacerw = int(w * buffer_percent)
  spacerh = int(h * buffer_percent)
  return [[x+spacerw, y+spacerh],
          [x+w-spacerw, y+spacerh]]

def face_points(classifier_folder, imgpath, add_boundary_points=True):
  """ Locates 77 face points using stasm (http://www.milbo.users.sonic.net/stasm)

  :param classifier_folder: path to folder containing the .xml classifier data
  :param imgpath: an image path to extract the 77 face points
  :param add_boundary_points: bool to add 2 additional points
  :returns: Array of x,y face points
  """
  command = './bin/stasm_util -f "{0}" "{1}"'.format(classifier_folder, imgpath)
  s = subprocess.check_output(command, shell=True)
  if s.startswith('No face found'):
    return []
  else:
    points = np.array([pair.split(' ') for pair in s.rstrip().split('\n')],
                      np.int32)
    if (add_boundary_points):
      points = np.vstack([points, boundary_points(points)])

    return points

def average_points(point_set):
  """ Averages a set of face points from images

  :param point_set: _n_ x _m_ x 2 array of face points.
  _n_ = number of images.
  _m_ = number of face points per image
  """
  return np.mean(point_set, 0).astype(np.int32)

def weighted_average_points(start_points, end_points, percent=0.5):
  """ Weighted average of two sets of supplied points

  :param start_points: _m_ x 2 array of start face points.
  :param end_points: _m_ x 2 array of end face points.
  :param percent: [0, 1] percentage weight on start_points
  :returns: _m_ x 2 array of weighted average points
  """
  if percent <= 0:
    return end_points
  elif percent >= 1:
    return start_points
  else:
    return np.asarray(start_points*percent + end_points*(1-percent), np.int32)

def roi_coordinates(rect, new_width, new_height, scale):
  """ Align the rectangle into the center of the new size.

  :param rect: x, y, w, h are the bounding rectangle of the face
  :param size: new width, new height are the dimensions of the crop
  :param scale: scaling factor of the rectangle to be resized
  :returns: top left (x, y) of the aligned ROI
  """
  rectx, recty, rectw, recth = rect
  mid_x = int((rectx + rectw/2) * scale)
  mid_y = int((recty + recth/2) * scale)
  roi_x = mid_x - new_width/2
  roi_y = mid_y - new_height/2
  return roi_x, roi_y

def resize(img, points, size):
  """ Resize image and associated points to the new supplied size

  :param img: image to be resized
  :param points: _m_ x 2 array of points
  :param size: (h, w) tuple of new size
  """
  cur_height, cur_width = img.shape[:2]
  new_height, new_width = size
  rect = cv2.boundingRect(np.array([points], np.int32))
  new_rectw = 0.6 * new_width
  scale = new_rectw / (rect[2] * 1.0)
  new_scaled_height = int(scale * cur_height)
  new_scaled_width = int(scale * cur_width)

  img = cv2.resize(img, (new_scaled_width, new_scaled_height))
  cur_height, cur_width = img.shape[:2]
  points[:, 0] *= scale
  points[:, 1] *= scale

  roi_x, roi_y = roi_coordinates(rect, new_width, new_height, scale)
  crop = np.zeros((new_height, new_width, 3), img.dtype)
  border_x = border_y = 0
  if roi_x < 0:
    border_x = abs(roi_x)
    roi_x = 0
  if roi_y < 0:
    border_y = abs(roi_y)
    roi_y = 0
  roi_h = min(new_height, cur_height-roi_y) - border_y
  roi_w = min(new_width, cur_width-roi_x) - border_x
  #print border_x, border_y, roi_x, roi_y, roi_w, roi_h, img.shape
  crop[border_y:border_y+roi_h, border_x:border_x+roi_w] = (
    img[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w])
  points[:, 0] += (border_x - roi_x)
  points[:, 1] += (border_y - roi_y)

  return (crop, points)
