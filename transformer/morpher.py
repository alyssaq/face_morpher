"""
::

  Morph from source to destination face

  Usage:
    morpher.py --src=<src_path> --dest=<dest_path> [--data=<classifiers_folder>] [--blend]

  Options:
    -h, --help             Show this screen.
    --blend                Boolean flag to blend images after averaging
    --version              Show version.
    --data=<folder>        Folder to .xmls for classifiers (default: ../data)
    --src=<src_imgpath>    Filepath to source image (.jpg, .jpeg, .png)
    --dest=<dest_path>     Filepath to destination image (.jpg, .jpeg, .png)
"""
from docopt import docopt
import numpy as np
import scipy.misc
from matplotlib import pyplot as plt

def plot_one(row, col, img, i):
  p = plt.subplot(row, col, i)
  p.axes.get_xaxis().set_visible(False)
  p.axes.get_yaxis().set_visible(False)
  plt.imshow(img)
  return i + 1

def plot_morph(data_folder, src_path, dest_path, do_blend=False):
  from functools import partial
  import scipy.ndimage
  import scipy.misc
  import locator
  import aligner
  import warper
  import blender

  plotter = partial(plot_one, 2, 7)
  # Load source image
  face_points_func = partial(locator.face_points, data_folder)
  src_img = scipy.ndimage.imread(src_path)[:, :, :3]

  # Define control points for warps
  src_points = face_points_func(src_path)
  dest_img = scipy.ndimage.imread(dest_path)[:, :, :3]
  dest_points = face_points_func(dest_path)

  size = (600, 500)
  src_img, src_points = aligner.resize_align(src_img, src_points, size)
  dest_img, dest_points = aligner.resize_align(dest_img, dest_points, size)

  i = plotter(src_img, 1)
  for percent in np.linspace(1, 0, num=5):
    points = locator.weighted_average_points(src_points, dest_points, percent)
    src_face = warper.warp_image(src_img, src_points, points, dest_img.shape[:2])

    i = plotter(src_face, i)

  mask = blender.mask_from_points(size, points)
  end_face = np.copy(dest_img)
  for c in range(3):
    end_face[..., c] = dest_img[..., c] * (mask/255)

  for percent in np.linspace(1, 0, num=5):
    ave = blender.weighted_average(src_face, end_face, percent)
    i = plotter(ave, i)

  print 'blending'
  blended_img = blender.poisson_blend(src_face, dest_img, mask)
  i = plotter(end_face, i)
  i = plotter(dest_img, i)
  i = plotter(blended_img, i)
  plt.gcf().subplots_adjust(hspace=0.05, wspace=0,
                            left=0, bottom=0, right=1, top=0.98)
  plt.axis('off')
  plt.show()

if __name__ == "__main__":
  args = docopt(__doc__, version='2 Image Morpher 1.0')
  if args['--data'] is None:
    args['--data'] = '../data'
  plot_morph(args['--data'], args['--src'], args['--dest'], args['--blend'])
  #plot_morph('../data', '../family/IMG_20140515_203547.jpg', '../john_malkovich.jpg', True)