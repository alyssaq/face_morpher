import cv2
import numpy as np
import subprocess

def boundary_points(points):
  """ Produce additional boundary points
  :param points: _n_ x 2 array of x,y points
  """
  x, y, w, h = cv2.boundingRect(np.array([points], np.int32))
  buffer_percent = 0.1
  spacerw = int(w * buffer_percent)
  spacerh = int(h * buffer_percent)
  return [[x+spacerw, y+spacerh],
          [x+w-spacerw, y+spacerh]]


def face_points(classifier_folder, imgpath, add_boundary_points=True):
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
