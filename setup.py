from setuptools import setup, find_packages
from setuptools.command.install import install
import os

# To test locally: python setup.py install
# To upload to pypi: python setup.py sdist bdist_wheel upload
class OverrideInstall(install):
  def run(self):
    install.run(self)  # install everything as per usual
    for filepath in self.get_outputs():
      if 'bin/stasm_util' in filepath:
        # make binaries executable
        os.chmod(filepath, 0o755)


setup(
  name='facemorpher',
  version='5.1.0',
  author='Alyssa Quek',
  author_email='alyssaquek@gmail.com',
  description=('Warp, morph and average human faces!'),
  keywords='face morphing, averaging, warping',
  url='https://github.com/alyssaq/face_morpher',
  license='MIT',
  packages=find_packages(),
  install_requires=[
    'docopt',
    'numpy',
    'scipy',
    'matplotlib',
    'stasm'
  ],
  cmdclass={'install': OverrideInstall},
  entry_points={'console_scripts': [
      'facemorpher=facemorpher.morpher:main',
      'faceaverager=facemorpher.averager:main'
    ]
  },
  data_files=[('readme', ['README.rst'])],
  long_description=open('README.rst').read(),
)
