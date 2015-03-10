"""
  Align face and image sizes
"""

import cv2
import numpy as np

def positive_cap(num):
  """ Cap a number to ensure it is positive

  :param num: positive or negative number
  :returns: (overflow, capped_number)
  """
  if num < 0:
    return 0, abs(num)
  else:
    return num, 0

def roi_coordinates(rect, size, scale):
  """ Align the rectangle into the center of the new size.

  :param rect: x, y, w, h are the bounding rectangle of the face
  :param size: new width, new height are the dimensions of the crop
  :param scale: scaling factor of the rectangle to be resized
  :returns: 4 numbers. top left coordinates of the aligned ROI.
    (x, y, border_x, border_y). All values are > 0.
  """
  rectx, recty, rectw, recth = rect
  new_height, new_width = size
  mid_x = int((rectx + rectw/2) * scale)
  mid_y = int((recty + recth/2) * scale)
  roi_x = mid_x - new_width/2
  roi_y = mid_y - new_height/2

  roi_x, border_x = positive_cap(roi_x)
  roi_y, border_y = positive_cap(roi_y)
  return roi_x, roi_y, border_x, border_y

def resize_align(img, points, size):
  """ Resize image and associated points and align to the new supplied size

  :param img: image to be resized
  :param points: _m_ x 2 array of points
  :param size: (h, w) tuple of new size
  """
  # Resize image based on bounding rectangle
  cur_height, cur_width = img.shape[:2]
  new_height, new_width = size
  rect = cv2.boundingRect(np.array([points], np.int32))
  new_rectw = 0.6 * new_width
  scale = new_rectw / (rect[2] * 1.0)
  new_scaled_height = int(scale * cur_height)
  new_scaled_width = int(scale * cur_width)
  img = cv2.resize(img, (new_scaled_width, new_scaled_height))

  # Align bounding rect to center and crop to supplied size
  cur_height, cur_width = img.shape[:2]
  roi_x, roi_y, border_x, border_y = roi_coordinates(rect, size, scale)
  crop = np.zeros((new_height, new_width, 3), img.dtype)

  roi_h = min(new_height, cur_height-roi_y) - border_y
  roi_w = min(new_width, cur_width-roi_x) - border_x
  # print border_x, border_y, roi_x, roi_y, roi_w, roi_h, img.shape
  crop[border_y:border_y+roi_h, border_x:border_x+roi_w] = (
    img[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w])
  points[:, 0] = (points[:, 0] * scale) + (border_x - roi_x)
  points[:, 1] = (points[:, 1] * scale) + (border_y - roi_y)

  return (crop, points)
