"""
::

  Mass face morpher

  Usage:
    mass_morpher.py --data=<classifiers_folder> --images=<images_folder>

  Options:
    -h, --help         Show this screen.
    --version          Show version.
    --data=<folder>    Folder to .xml data for classifiers
    --images=<folder>  Folder to images (.jpg, .jpeg, .png)

"""
from docopt import docopt
import os
import morpher
#import warp_affine
import scipy.ndimage
from matplotlib import pyplot as plt
import cv2
import numpy as np
from random import shuffle
from functools import partial
  
def list_imgpaths(imgfolder):
  for fname in os.listdir(imgfolder):
    if (fname.lower().endswith('.jpg') or
        fname.lower().endswith('.png') or
        fname.lower().endswith('.jpeg')):
      yield os.path.join(imgfolder, fname)

def sharpen(img):
  blured = cv2.GaussianBlur(img, (0, 0), 2.5)
  return cv2.addWeighted(img, 1.4, blured, -0.4, 0)

def main():
  args = docopt(__doc__, version='Morpher 1.0')
  imgpaths = list(list_imgpaths(args['--images'])) #list(list_imgpaths('males')) #+ list(list_imgpaths('females'))
  #shuffle(imgpaths)

  face_points_func = partial(morpher.face_points, args['--data'])
  percent = 1 / (len(imgpaths) + 1.0)
  basepath = '../base/female_average.jpg'
  dst_img = scipy.ndimage.imread(basepath)
  base_points = face_points_func(basepath)
  base_img = np.copy(dst_img)

  passed = failed = 0
  dst_img = np.asarray(dst_img * percent, np.uint8)
  for i, path in enumerate(imgpaths):
    print i, path

    src_img = scipy.ndimage.imread(path)
    src_points = face_points_func(path)
    if len(src_points) == 0:
      print 'No face'
      failed += 1
      continue

    result_img = morpher.warp_image(src_img, src_points, base_img, base_points)
    #dst_img = cv2.addWeighted(dst_img, 0.6, result_img, 0.4, 0)
    dst_img += np.asarray(result_img * percent, np.uint8)
    passed += 1

  dst_img = sharpen(dst_img)

  #cv::addWeighted(frame, 1.5, image, -0.5, 0, image);)
  print 'Processed {0} face. {1} failed.'.format(passed, failed)
  plt.axis('off')
  plt.imshow(dst_img)
  plt.show()

if __name__ == "__main__":
  main()
