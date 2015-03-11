"""
::

  Face averager

  Usage:
    averager.py --images=<images_folder> [--blend] [--data=<classifiers_folder>]
              [--width=<width>] [--height=<height>]

  Options:
    -h, --help         Show this screen.
    --images=<folder>  Folder to images (.jpg, .jpeg, .png)
    --blend            Flag to blend images [default: False]
    --width=<width>    Custom width of the images/video [default: 500]
    --height=<height>  Custom height of the images/video [default: 600]
    --data=<folder>    Folder to .xmls for classifiers [default: data]
    --version          Show version.
"""
from docopt import docopt
import os
import cv2
import numpy as np
import scipy.ndimage
from functools import partial
from matplotlib import pyplot as plt
import matplotlib.image as mpimg

import locator
import warper

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
  imgpaths = list(list_imgpaths(args['--images']))

  face_points_func = partial(locator.face_points, args['--data'])
  basepath = imgpaths[5]
  base_img = scipy.ndimage.imread(basepath)
  base_points = face_points_func(basepath)

  passed = failed = 0
  images = np.zeros(base_img.shape, np.float32)
  for i, path in enumerate(imgpaths):
    print i, path

    src_img = scipy.ndimage.imread(path)
    src_points = face_points_func(path)
    if len(src_points) == 0:
      print 'No face'
      failed += 1
      continue

    images += warper.warp_image(src_img, src_points,
                                base_points, base_img.shape[:2])
    passed += 1

  result_image = np.uint8(images / passed)

  if args['--blend']:
    result_image = sharpen(result_image)
    import blender
    mask = blender.mask_from_points(base_img.shape[:2], base_points)
    result_image = blender.alpha_feathering(base_img, result_image, mask)

  print 'Processed {0} face. {1} failed.'.format(passed, failed)
  plt.axis('off')
  plt.imshow(result_image)
  plt.show()
  mpimg.imsave('result.png', result_image)

if __name__ == "__main__":
  main()
