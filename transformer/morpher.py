import numpy as np
import scipy.misc
from matplotlib import pyplot as plt

def plot_one(row, col, img, i):
  p = plt.subplot(row, col, i)
  p.axes.get_xaxis().set_visible(False)
  p.axes.get_yaxis().set_visible(False)
  plt.imshow(img)
  return i + 1

def test_local():
  from functools import partial
  import scipy.ndimage
  import scipy.misc
  import locator
  import aligner
  import warper
  import blender

  plotter = partial(plot_one, 2, 7)
  # Load source image
  face_points_func = partial(locator.face_points, '../data')
  base_path = '../john_malkovich.jpg'
  src_path = '../family/IMG_20140515_203547.jpg'
  src_img = scipy.ndimage.imread(src_path)[:, :, :3]

  # Define control points for warps
  src_points = face_points_func(src_path)
  base_img = scipy.ndimage.imread(base_path)[:, :, :3]
  base_points = face_points_func(base_path)

  size = (600, 500)
  src_img, src_points = aligner.resize_align(src_img, src_points, size)
  base_img, base_points = aligner.resize_align(base_img, base_points, size)

  i = plotter(src_img, 1)
  for percent in np.linspace(1, 0, num=5):
    points = locator.weighted_average_points(src_points, base_points, percent)
    src_face = warper.warp_image(src_img, src_points, points, base_img.shape[:2])

    i = plotter(src_face, i)
  
  mask = blender.mask_from_points(size, points)
  end_face = np.copy(base_img)
  for c in range(3):
    end_face[..., c] = base_img[..., c] * (mask/255)

  for percent in np.linspace(1, 0, num=5):
    ave = blender.weighted_average(src_face, end_face, percent)
    i = plotter(ave, i)

  print 'blending'
  blended_img = blender.poisson_blend(src_face, base_img, mask)
  i = plotter(end_face, i)
  i = plotter(base_img, i)
  i = plotter(blended_img, i)
  plt.gcf().subplots_adjust(hspace=0.05, wspace=0,
                            left=0, bottom=0, right=1, top=0.98)
  plt.axis('off')
  plt.show()

if __name__ == "__main__":
  test_local()
