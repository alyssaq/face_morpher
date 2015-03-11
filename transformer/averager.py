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
import aligner
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

def load_image_points(data_folder, path, size):
  img = scipy.ndimage.imread(path)[..., :3]
  points = locator.face_points(data_folder, path)

  if len(points) == 0:
    return None, None
  else:
    return aligner.resize_align(img, points, size)

def average_faces(images_folder, data_folder, width=500, height=600,
                  blend=False):
  imgpaths = list(list_imgpaths(images_folder))

  size = (height, width)
  loader = partial(load_image_points, data_folder, size=size)

  images = []
  point_set = []
  for path in imgpaths:
    img, points = loader(path)
    if img is not None:
      images.append(img)
      point_set.append(points)

  ave_points = locator.average_points(point_set)
  num_images = len(images)
  result_images = np.zeros(images[0].shape, np.float32)
  for i in xrange(num_images):
    print '{0} of {1}'.format(i+1, num_images)

    result_images += warper.warp_image(images[i], point_set[i],
                                       ave_points, size)

  result_image = np.uint8(result_images / num_images)

  if blend:
    result_image = sharpen(result_image)
    import blender
    mask = blender.mask_from_points(base_img.shape[:2], base_points)
    result_image = blender.alpha_feathering(base_img, result_image, mask)

  print 'Processed {0} faces'.format(num_images)
  plt.axis('off')
  plt.imshow(result_image)
  plt.show()
  mpimg.imsave('result.png', result_image)

if __name__ == "__main__":
  args = docopt(__doc__, version='Face Averager 1.0')
  average_faces(args['--images'], args['--data'],
                int(args['--width']), int(args['--height']), args['--blend'])
