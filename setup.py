from distutils.core import setup

setup(
  name='facemorpher',
  version='0.0.7-dev',
  author='Alyssa Quek',
  author_email='alyssaquek@gmail.com',
  description=('Warp, morph and average human faces!'),
  packages=['transformer'],
  package_data={'transformer': ['data/*.xml', 'bin/stasm_util']},
  data_files=[('readme', ['README.rst'])],
  keywords='face morphing, averaging, warping',
  url='https://github.com/alyssaq/face_morpher',
  long_description=open('README.rst').read(),
  license='MIT',
)
