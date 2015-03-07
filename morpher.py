import numpy as np
import scipy.spatial as spatial
import cv2
import subprocess
import scipy.ndimage
from matplotlib import pyplot as plt
from functools import partial
import scipy.ndimage.measurements

def bilinear_interpolate(img, coords):
  """
  http://en.wikipedia.org/wiki/Bilinear_interpolation
  """
  int_coords = np.int32(coords)
  x0, y0 = int_coords
  dx, dy = coords - int_coords

  # Interpolate over every image channel
  q11 = img[y0, x0]
  q21 = img[y0, x0+1]
  q12 = img[y0+1, x0]
  q22 = img[y0+1, x0+1]

  btm = dx * q21 + (1. - dx) * q11
  top = dx * q22 + (1. - dx) * q12
  inter_pixel = dy * top + (1. - dy) * btm

  return inter_pixel

def bilinear_interpolate_arr(img, coords):
  """
  http://en.wikipedia.org/wiki/Bilinear_interpolation

  Input
  -----
  img: max 3 channel image
  coords: 2 x m array. 1st row = xcoords, 2nd row = ycoords
  """
  int_coords = np.int32(coords)
  x0, y0 = int_coords
  dx, dy = coords - int_coords

  # Interpolate over every image channel
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
          np.max(points[:, 0]),
          np.min(points[:, 1]),
          np.max(points[:, 1])]

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
    result_img[y, x] = bilinear_interpolate_arr(src_img, out_coords)

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
    # mat = cv2.getAffineTransform(
    #   (base_points[tri_indices, :]),
    #   (src_points[tri_indices, :]))

    src_tri = np.vstack((src_points[tri_indices, :].T, ones))
    dst_tri = np.vstack((base_points[tri_indices, :].T, ones))
    mat = np.dot(src_tri, np.linalg.inv(dst_tri))[:2, :]
    yield mat

def rect_points(points):
  x, y, w, h = cv2.boundingRect(np.array([points], np.int32))
  spacerw = int(w * 0.1)
  spacerh = int(h * 0.1)
  return [[x+spacerw, y+spacerh],
          [x+w-spacerw, y+spacerh]]

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

def face_points(classifier_folder, imgpath):
  command = './bin/stasm_util -f {0} "{1}"'.format(classifier_folder, imgpath)
  s = subprocess.check_output(command, shell=True)
  if s.startswith("No face found"):
    return []
  else:
    return np.array([pair.split(' ') for pair in s.rstrip().split('\n')],
                    np.int32)

def main():
  #Load source image
  face_points_func = partial(face_points, 'data')
  base_path = 'females/face1.jpeg'
  srcIm_path = 'twba/+Foto am 02.03.15 _ 10 um 16.57.jpg'
  src2Im_path = 'females/face1.jpg'
  src2 = scipy.ndimage.imread(src2Im_path)
  src2_points = face_points_func(src2Im_path)
  src1 = scipy.ndimage.imread(srcIm_path)
  
  src1_points = face_points_func(srcIm_path)
  baseIm = scipy.ndimage.imread(base_path)
  base_points = face_points_func(base_path)
  #Define control points for warps

  #Perform transform
  dstIm = warp_image(src1, src1_points, baseIm, base_points)
  ave = cv2.addWeighted(baseIm, 0.5, dstIm, 0.5, 0)

  #dstIm2 = morph_image(src1, src2_points, baseIm, base_points)
  #ave2 = cv2.addWeighted(ave, 0.5, dstIm2, 0.5, 0)

  plt.subplot(2,2,1)
  plt.imshow(baseIm)
  plt.subplot(2,2,2)
  plt.imshow(dstIm)
  plt.subplot(2,2,3)
  plt.imshow(ave)
  #plt.subplot(2,2,4)
  #plt.imshow(ave2)
 # plt.show()
  #cv2.imshow('img', PIL2array(dstIm))
  #cv2.waitKey(0)
  #cv2.destroyAllWindows()
  #Visualise result
  #dstIm.show()

if __name__ == "__main__":
  main()

  
