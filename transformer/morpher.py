import numpy as np
import scipy.spatial as spatial
import cv2
import scipy.ndimage
import scipy.misc
from matplotlib import pyplot as plt
from functools import partial
import scipy.ndimage.measurements
import locator

def bilinear_interpolate(img, coords):
  """ Interpolates over every image channel
  http://en.wikipedia.org/wiki/Bilinear_interpolation
  
  :param img: max 3 channel image
  :param coords: 2 x _m_ array. 1st row = xcoords, 2nd row = ycoords
  :returns: array of interpolated pixels with same shape as coords
  """
  int_coords = np.int32(coords)
  x0, y0 = int_coords
  dx, dy = coords - int_coords

  # 4 Neighour pixels
  q11 = img[y0, x0]
  q21 = img[y0, x0+1]
  q12 = img[y0+1, x0]
  q22 = img[y0+1, x0+1]

  btm = q21.T * dx + q11.T * (1 - dx)
  top = q22.T * dx + q12.T * (1 - dx)
  inter_pixel = top * dy + btm * (1 - dy)

  return inter_pixel.T

def min_max(points):
  return [np.min(points[:, 0]),
          np.max(points[:, 0]) + 1,
          np.min(points[:, 1]),
          np.max(points[:, 1]) + 1]

def process_warp(src_img, result_img, tri_affines, dst_points, delaunay):
  """
  Warp each triangle from the src_image only within the
  ROI of the destination image (points in dst_points).
  """
  xmin, xmax, ymin, ymax = min_max(dst_points)
  # [(x, y)] to pixels within ROI
  roi_coords = np.asarray([(x, y) for y in xrange(ymin, ymax)
                          for x in xrange(xmin, xmax)], np.int32)
  # indices to vertices. -1 if pixel is not in any triangle
  roi_tri_indices = delaunay.find_simplex(roi_coords)

  for simplex_index in xrange(len(delaunay.simplices)):
    coords = roi_coords[roi_tri_indices == simplex_index]
    num_coords = len(coords)
    out_coords = np.dot(tri_affines[simplex_index],
                        np.vstack((coords.T, np.ones(num_coords))))
    x, y = coords.T
    result_img[y, x] = bilinear_interpolate(src_img, out_coords)

  return None

def triangular_affine_matrices(vertices, src_points, base_points):
  """
  Calculate the affine transformation matrix for each triangle vertex
  from base_points to src_points

  Input
  ---
  vertices: array of triplet indices to corners of triangle
  src_points: array of [x, y] points to landmarks for source image
  base_points: array of [x, y] points to landmarks for destination image
  """
  ones = [1, 1, 1]
  for tri_indices in vertices:
    src_tri = np.vstack((src_points[tri_indices, :].T, ones))
    dst_tri = np.vstack((base_points[tri_indices, :].T, ones))
    mat = np.dot(src_tri, np.linalg.inv(dst_tri))[:2, :]
    yield mat

def warp_image(src_img, src_points, base_img, base_points):
  base_points = np.vstack([base_points, rect_points(base_points)])
  src_points = np.vstack([src_points, rect_points(src_points)])
  delaunay = spatial.Delaunay(base_points)

  tri_affines = np.asarray(list(triangular_affine_matrices(
    delaunay.simplices, src_points, base_points)))

  # Resultant image will not have an alpha channel
  src_img = src_img[:, :, :3]
  result_img = np.copy(base_img[:, :, :3])

  process_warp(src_img, result_img, tri_affines, base_points, delaunay)

  return result_img

def save_mask(base_img, base_points):
  radius = 15  # kernel size
  kernel = np.ones((radius, radius), np.uint8)

  base_points = np.vstack([base_points, rect_points(base_points)])
  mask = np.zeros(base_img.shape[:2], np.uint8)
  cv2.fillConvexPoly(mask, cv2.convexHull(base_points), 255)
  mask = cv2.erode(mask, kernel)

  cv2.imwrite('mask.jpg', mask)
  #print 'mask saved'
  return mask

def blend(dest_img, base_img, base_points):
  radius = 15  # kernel size
  kernel = np.ones((radius, radius), np.uint8)

  base_points = np.vstack([base_points, rect_points(base_points)])
  mask = np.zeros(base_img.shape[:2], np.uint8)
  cv2.fillConvexPoly(mask, cv2.convexHull(base_points), 255)
  mask = cv2.erode(mask, kernel)

  mask = cv2.blur(mask, (15, 15))
  mask = mask / 255.0

  result_img = np.empty(base_img.shape, np.uint8)
  for i in xrange(3):
    result_img[..., i] = dest_img[..., i] * mask + base_img[..., i] * (1-mask)

  return result_img

def main():
  #Load source image
  face_points_func = partial(locator.face_points, '../data')
  base_path = '../base/female_average.jpg'
  src_path = '../females/long-face.jpg'
  src = scipy.ndimage.imread(src_path)
  
  #Define control points for warps
  src_points = face_points_func(src_path)
  base_img = scipy.ndimage.imread(base_path)
  base_points = face_points_func(base_path)

  #Perform transform
  dst_img = warp_image(src, src_points, base_img, base_points)
  ave = cv2.addWeighted(base_img, 0.5, dst_img, 0.5, 0)
  blended_img = blend(dst_img, base_img, base_points)

  save_mask(base_img, base_points)
  scipy.misc.imsave('dest.jpg', dst_img)
  scipy.misc.imsave('dest2.jpg', ave)
  plt.subplot(2,2,1)
  plt.imshow(base_img)
  plt.subplot(2,2,2)
  plt.imshow(dst_img)
  plt.subplot(2,2,3)
  plt.imshow(ave)
  plt.subplot(2,2,4)
  plt.imshow(blended_img)
  plt.show()

  #cv2.waitKey(0)
  #cv2.destroyAllWindows()

if __name__ == "__main__":
  main()

  
