"""
Create a video with image frames
"""

import cv2
import numpy as np

def check_write_video(func):
  def inner(self, *args, **kwargs):
    if self.video:
      return func(self, *args, **kwargs)
    else:
      pass
  return inner


class Video(object):
  def __init__(self, filename, num_frames, size):
    fourcc = cv2.cv.FOURCC('m', 'p', '4', 'v')
    self.filename = filename
    self.counter = 0
    self.num_frames = num_frames

    if filename is None:
      self.video = None
    else:
      self.video = cv2.VideoWriter(filename, fourcc, num_frames, size, True)

  @check_write_video
  def write(self, img):
    frame = np.copy(img)
    if img.shape[2] == 3:
      #  OpenCV channels are gbr so we need to swap scipy's rgb chs
      frame[..., 0], frame[..., 2] = img[..., 2], img[..., 0]

    self.video.write(frame)
    self.counter += 1
    if self.counter == self.num_frames:
      self.end()

  @check_write_video
  def end(self):
    print self.filename, 'saved'
    self.video.release()
