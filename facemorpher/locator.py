"""
Locate face points
"""

import cv2
import numpy as np
import subprocess
import os.path as path

def boundary_points(points):
  """ Produce additional boundary points

  :param points: *m* x 2 array of x,y points
  :returns: 2 additional points at the top corners
  """
  x, y, w, h = cv2.boundingRect(np.array([points], np.int32))
  buffer_percent = 0.1
  spacerw = int(w * buffer_percent)
  spacerh = int(h * buffer_percent)
  return [[x+spacerw, y+spacerh],
          [x+w-spacerw, y+spacerh]]

def face_points(imgpath, add_boundary_points=True):
  """ Locates 77 face points using stasm (http://www.milbo.users.sonic.net/stasm)

  :param imgpath: an image path to extract the 77 face points
  :param add_boundary_points: bool to add 2 additional points
  :returns: Array of x,y face points. Empty array if no face found
  """
  directory = path.dirname(path.realpath(__file__))
  stasm_path = path.join(directory, 'bin/stasm_util')
  data_folder = path.join(directory, 'data')
  command = '"{0}" -f "{1}" "{2}"'.format(stasm_path, data_folder, imgpath)
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

  :param point_set: *n* x *m* x 2 array of face points. \\
  *n* = number of images. *m* = number of face points per image
  """
  return np.mean(point_set, 0).astype(np.int32)

def weighted_average_points(start_points, end_points, percent=0.5):
  """ Weighted average of two sets of supplied points

  :param start_points: *m* x 2 array of start face points.
  :param end_points: *m* x 2 array of end face points.
  :param percent: [0, 1] percentage weight on start_points
  :returns: *m* x 2 array of weighted average points
  """
  if percent <= 0:
    return end_points
  elif percent >= 1:
    return start_points
  else:
    return np.asarray(start_points*percent + end_points*(1-percent), np.int32)
