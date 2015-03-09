"""
Locate face points
"""

import cv2
import numpy as np
import subprocess

def boundary_points(points):
  """ Produce additional boundary points

  :param points: _n_ x 2 array of x,y points
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
