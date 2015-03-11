"""
::

  Morph from source to destination face

  Usage:
    morpher.py --src=<src_path> --dest=<dest_path> [--data=<classifiers_folder>] [--blend]

  Options:
    -h, --help             Show this screen.
    --src=<src_imgpath>    Filepath to source image (.jpg, .jpeg, .png)
    --dest=<dest_path>     Filepath to destination image (.jpg, .jpeg, .png)
    --blend                Flag to blend images after averaging (default: False)
    --data=<folder>        Folder to .xmls for classifiers (default: data)
    --version              Show version.
"""

from docopt import docopt
import scipy.ndimage
import numpy as np
from functools import partial
import plotter

def plot_morph(data_folder, src_path, dest_path, num_frames=20, blend=False):
  import scipy.misc
  import locator
  import aligner
  import warper
  import blender

  num_frames += (1 if blend else 0)
  plt = plotter.Plotter(True, num_images=num_frames)
  num_frames -= 2  # No need to plot/save src and dest image

  # Load source image
  face_points_func = partial(locator.face_points, data_folder)
  src_img = scipy.ndimage.imread(src_path)[:, :, :3]
  src_points = face_points_func(src_path)
  dest_img = scipy.ndimage.imread(dest_path)[:, :, :3]
  dest_points = face_points_func(dest_path)

  size = (600, 500)
  src_img, src_points = aligner.resize_align(src_img, src_points, size)
  dest_img, dest_points = aligner.resize_align(dest_img, dest_points, size)
  mask = blender.mask_from_points(size, dest_points)

  plt.plot_one(src_img)
  for percent in np.linspace(1, 0, num=num_frames):
    points = locator.weighted_average_points(src_points, dest_points, percent)
    src_face = warper.warp_image(
      src_img, src_points, points, dest_img.shape[:2])
    end_face = warper.warp_image(
      dest_img, dest_points, points, dest_img.shape[:2])
    average_face = blender.weighted_average(src_face, end_face, percent)
    plt.plot_one(average_face, 'save')
  plt.plot_one(dest_img)

  if do_blend:
    print 'blending'
    blended_img = blender.poisson_blend(src_face, dest_img, mask)
    plt.plot_one(blended_img)

  plt.show()

if __name__ == "__main__":
  # args = docopt(__doc__, version='2 Image Morpher 1.0')
  # if args['--data'] is None:
  #   args['--data'] = 'data'
  # plot_morph(args['--data'], args['--src'], args['--dest'], args['--blend'])
  plot_morph('../data', '../family/IMG_20140515_203547.jpg', '../john_malkovich.jpg', 4, False)