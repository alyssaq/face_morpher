from distutils.core import setup

setup(
  name='facemorpher',
  version='2.0.0',
  author='Alyssa Quek',
  author_email='alyssaquek@gmail.com',
  description=('Warp, morph and average human faces!'),
  packages=['facemorpher'],
  package_data={'facemorpher': [
    'data/*.xml',
    'bin/stasm_util_osx_cv2',
    'bin/stasm_util_osx_cv3',
    'bin/stasm_util_linux_cv2'
  ]},
  data_files=[('readme', ['README.rst'])],
  keywords='face morphing, averaging, warping',
  url='https://github.com/alyssaq/face_morpher',
  long_description=open('README.rst').read(),
  license='MIT',
)
