import numpy as np
import scipy.spatial as spatial
import cv2
import subprocess
import scipy.ndimage
from matplotlib import pyplot as plt
from functools import partial
import multiprocessing as mp

def bilinear_interpolate(img, x, y):
  """
  http://en.wikipedia.org/wiki/Bilinear_interpolation
  """
  x0 = np.floor(x).astype(int)
  y0 = np.floor(y).astype(int)
  x1 = x - x0
  y1 = y - y0

  # Interpolate for each image channel (no more than 3 channels)
  num_channels = np.clip(img.shape[2], 1, 3)
  result = np.empty(num_channels, np.uint8)
  for chan in range(num_channels):
    # pixels at the four corners
    q11 = img[y0, x0, chan]
    q21 = img[y0, x0+1, chan]
    q12 = img[y0+1, x0, chan]
    q22 = img[y0+1, x0+1, chan]

    btm = x1 * q21 + (1. - x1) * q11
    top = x1 * q22 + (1. - x1) * q12
    inter_p = y1 * top + (1. - y1) * btm
    result[chan] = int(inter_p)

  return result

def rect_points(points):
  x, y, w, h = cv2.boundingRect(np.array([points], np.int32))
  spacerw = int(w * 0.1)
  spacerh = int(h * 0.1)
  return [[x+spacerw, y+spacerh],
          [x+w-spacerw, y+spacerh]]

def min_max(points):
  return [np.min(points[:, 0]),
          np.max(points[:, 0]),
          np.min(points[:, 1]),
          np.max(points[:, 1])]

def transform_pixel(src_img, result_img, tri_affines, delaunay, x, y):
  # Process pixels that are in a tesselation triangle
  print x, y
  tri_index = delaunay.find_simplex([x, y])
  if tri_index == -1: return

  # Affine transform and interpolate the pixel
  out = np.dot(tri_affines[tri_index], np.array([x, y, 1]))
  return bilinear_interpolate(src_img, out[0], out[1])

def process_warp_processes(src_img, result_img, tri_affines, dst_points, delaunay):
  transform_pixel_func = partial(transform_pixel, src_img, result_img, tri_affines, delaunay)
  xmin, xmax, ymin, ymax = min_max(dst_points)

  pool = mp.Pool(processes=10)
  results = [pool.apply(transform_pixel_func, args=(x,y,)) for y in range(ymin, ymax + 1) for x in range(xmin, xmax + 1)]
  results.reshape((ymax+1-ymin, xmax+1-xmin, 3))
  print results.shape
  return result_img

def process_warp(src_img, result_img, tri_affines, dst_points, delaunay):
  # Warp within the rect ROI of src image
  xmin, xmax, ymin, ymax = min_max(dst_points)
  for x in range(xmin, xmax + 1):
    for y in range(ymin, ymax + 1):
      # Process pixels that are in a tesselation triangle
      tri_index = delaunay.find_simplex([x, y])
      if tri_index == -1: continue

      # Affine transform and interpolate the pixel
      out = np.dot(tri_affines[tri_index], np.array([x, y, 1]))
      result_img[y, x] = bilinear_interpolate(src_img, out[0], out[1])

  return None

def triangular_affine_matrices(vertices, src_points, base_points):
  """
  Calculate the affine transformation matrix for each triangle vertex

  Input
  ---
  vertices: array of triplet indices to corners of triangle
  src_points: array of [x, y] points to landmarks for source image
  base_points: array of [x, y] points to landmarks for destination image
  """
  for tri_indices in vertices:
    src_tri = np.vstack((src_points[tri_indices, :].T, np.ones(3)))
    dst_tri = np.vstack((base_points[tri_indices, :].T, np.ones(3)))
    yield np.dot(src_tri, np.linalg.inv(dst_tri))

def warp_image(src_img, src_points, base_img, base_points):
  base_points = np.vstack([base_points, rect_points(base_points)])
  src_points = np.vstack([src_points, rect_points(src_points)])
  delaunay = spatial.Delaunay(base_points)

  # Find all triangle affine mapping from src to dest
  tri_affines = list(triangular_affine_matrices(
    delaunay.simplices, src_points, base_points))

  # Resultant image will not have an alpha channel
  dims = cv2.split(base_img)
  result_img = cv2.merge(dims[:3])

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

if __name__ == "__main__":
  from functools import partial
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
  plt.show()
  #cv2.imshow('img', PIL2array(dstIm))
  #cv2.waitKey(0)
  #cv2.destroyAllWindows()
  #Visualise result
  #dstIm.show()

  
