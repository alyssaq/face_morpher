"""
::

  Morph from source to destination face

  Usage:
    morpher.py (--src=<src_path> --dest=<dest_path> | --images=<folder>)
              [--width=<width>] [--height=<height>]
              [--num=<num_frames>] [--fps=<frames_per_second>]
              [--out_frames=<folder>] [--out_video=<filename>]
              [--plot] [--blend]

  Options:
    -h, --help              Show this screen.
    --src=<src_imgpath>     Filepath to source image (.jpg, .jpeg, .png)
    --dest=<dest_path>      Filepath to destination image (.jpg, .jpeg, .png)
    --images=<folder>       Folder to images
    --width=<width>         Custom width of the images/video [default: 500]
    --height=<height>       Custom height of the images/video [default: 600]
    --num=<num_frames>      Number of morph frames [default: 20]
    --fps=<fps>             Number frames per second for the video [default: 10]
    --out_frames=<folder>   Folder path to save all image frames
    --out_video=<filename>  Filename to save a video
    --plot                  Flag to plot images [default: False]
    --blend                 Flag to blend images [default: False]
    --version               Show version.
"""

from docopt import docopt
import scipy.ndimage
import numpy as np
import os
import locator
import aligner
import warper
import blender
import plotter
import videoer

def verify_args(args):
  if args['--images'] is None:
    valid = os.path.isfile(args['--src']) & os.path.isfile(args['--dest'])
    if not valid:
      print('--src=%s or --dest=%s are not valid images' % (
        args['--src'], args['--dest']))
      exit(1)
  else:
    valid = os.path.isdir(args['--images'])
    if not valid:
      print('--images=%s is not a valid directory' % args['--images'])
      exit(1)

def load_image_points(path, size):
  img = scipy.ndimage.imread(path)[..., :3]
  points = locator.face_points(path)

  if len(points) == 0:
    print 'No face in image %s' % path
    exit(1)
  else:
    return aligner.resize_align(img, points, size)

def morph(src_path, dest_path, width=500, height=600,
          num_frames=20, fps=10, out_frames=None, out_video=None,
          blend=False, plot=False):
  size = (height, width)
  stall_frames = np.clip(int(fps*0.15), 1, fps)  # Show first & last longer
  video = videoer.Video(out_video, num_frames,
                        fps, width, height)
  num_frames += (1 if blend else 0)
  plt = plotter.Plotter(plot, num_images=num_frames, folder=out_frames)
  num_frames -= (stall_frames * 2)  # No need to process src and dest image

  src_img, src_points = load_image_points(src_path, size)
  dest_img, dest_points = load_image_points(dest_path, size)

  plt.plot_one(src_img)
  video.write(src_img, stall_frames)

  # Produce morph frames!
  for percent in np.linspace(1, 0, num=num_frames):
    points = locator.weighted_average_points(src_points, dest_points, percent)
    src_face = warper.warp_image(src_img, src_points, points, size)
    end_face = warper.warp_image(dest_img, dest_points, points, size)
    average_face = blender.weighted_average(src_face, end_face, percent)
    plt.plot_one(average_face, 'save')
    video.write(average_face)

  plt.plot_one(dest_img)
  video.write(dest_img, stall_frames)

  if blend:
    print('blending')
    mask = blender.mask_from_points(size, dest_points)
    blended_img = blender.poisson_blend(src_face, dest_img, mask)
    plt.plot_one(blended_img)

  plt.show()

def test():
  morph('../data', '../family/IMG_20140515_203547.jpg',
        '../john_malkovich.jpg', 4, 600, 550, out_frames='test')

if __name__ == "__main__":
  args = docopt(__doc__, version='2 Image Morpher 1.0')
  verify_args(args)

  morph(args['--src'], args['--dest'],
        int(args['--width']), int(args['--height']),
        int(args['--num']), int(args['--fps']),
        args['--out_frames'], args['--out_video'],
        args['--blend'], args['--plot'])
