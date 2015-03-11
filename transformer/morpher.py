"""
::

  Morph from source to destination face

  Usage:
    morpher.py --src=<src_path> --dest=<dest_path>
               --width=<width> --height=<height>
              [--num=<num_frames>] [--blend]
              [--out_frames=<folder>] [--out_video=<filename>]
              [--data=<classifiers_folder>]

  Options:
    -h, --help              Show this screen.
    --src=<src_imgpath>     Filepath to source image (.jpg, .jpeg, .png)
    --dest=<dest_path>      Filepath to destination image (.jpg, .jpeg, .png)
    --num=<num_frames>      Number of morph frames (default: 20)
    --out_frames=<folder>   Folder path to save all image frames
    --out_video=<filename>  Filename to save a video (e.g. output.avi)
    --blend                 Flag to blend images (default: False)
    --data=<folder>         Folder to .xmls for classifiers (default: data)
    --version               Show version.
"""

from docopt import docopt
import scipy.ndimage
import numpy as np
from functools import partial
import locator
import aligner
import warper
import blender
import plotter
import videoer

def load_image_points(data_folder, path, size):
  img = scipy.ndimage.imread(path)[..., :3]
  points = locator.face_points(data_folder, path)

  return aligner.resize_align(img, points, size)

def morph(data_folder, src_path, dest_path, num_frames=20,
          width=500, height=600, out_frames=None, out_video=None, blend=False):

  size = (height, width)
  video = videoer.Video(out_video, num_frames, width, height)
  num_frames += (1 if blend else 0)
  plt = plotter.Plotter(True, num_images=num_frames, folder=out_frames)
  num_frames -= 2  # No need to plot/save src and dest image

  loader = partial(load_image_points, data_folder, size=size)
  src_img, src_points = loader(src_path)
  dest_img, dest_points = loader(dest_path)

  plt.plot_one(src_img)
  video.write(src_img)

  for percent in np.linspace(1, 0, num=num_frames):
    points = locator.weighted_average_points(src_points, dest_points, percent)
    src_face = warper.warp_image(src_img, src_points, points, size)
    end_face = warper.warp_image(dest_img, dest_points, points, size)
    average_face = blender.weighted_average(src_face, end_face, percent)
    plt.plot_one(average_face, 'save')
    video.write(average_face)

  plt.plot_one(dest_img)
  video.write(dest_img)

  if blend:
    print 'blending'
    mask = blender.mask_from_points(size, dest_points)
    blended_img = blender.poisson_blend(src_face, dest_img, mask)
    plt.plot_one(blended_img)

  plt.show()

if __name__ == "__main__":
  # args = docopt(__doc__, version='2 Image Morpher 1.0')
  # if args['--data'] is None:
  #   args['--data'] = 'data'
  # morph(args['--data'], args['--src'], args['--dest'], args['--blend'])
  morph('../data', '../family/IMG_20140515_203547.jpg', 
        '../john_malkovich.jpg', 4,
         600, 550, 
        out_frames='test',out_video='output.avi')
