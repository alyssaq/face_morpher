import cv2

def is_cv2():
  return cv2.__version__.startswith('2.')

def is_cv3():
  return cv2.__version__.startswith('3.')

def version():
  (major, minor, patch) = cv2.__version__.split('.')[:3]
  return '.'.join([major, minor, patch])
