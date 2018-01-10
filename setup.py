from setuptools import setup, find_packages
from setuptools.command.install import install
import os

# To test locally: python setup.py install
# To upload to pypi: python setup.py sdist upload
class OverrideInstall(install):
  def run(self):
    uid, gid = 0, 0
    mode = '0700'
    install.run(self) # install everything as per usual
    for filepath in self.get_outputs():
      if 'bin/stasm_util' in filepath:
        # make binaries executable
        os.chmod(filepath, 0o755)

setup(
  name='facemorpher',
  version='3.2.0',
  author='Alyssa Quek',
  author_email='alyssaquek@gmail.com',
  description=('Warp, morph and average human faces!'),
  keywords='face morphing, averaging, warping',
  url='https://github.com/alyssaq/face_morpher',
  license='MIT',
  packages=find_packages(),
  package_data={'facemorpher': [
    'data/*.xml',
    'bin/stasm_util_osx_cv3.2',
    'bin/stasm_util_osx_cv3.4',
    'bin/stasm_util_linux_cv3.2',
    'bin/stasm_util_linux_cv3.4'
  ]},
  cmdclass={'install': OverrideInstall},
  entry_points={'console_scripts': [
      'facemorpher=facemorpher.morpher:main',
      'faceaverager=facemorpher.averager:main'
    ]
  },
  data_files=[('readme', ['README.rst'])],
  long_description=open('README.rst').read(),
)
