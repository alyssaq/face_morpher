#!/bin/bash

rm -rf docs
# reStructuredText in python files to rst. Documentation in docs folder
sphinx-apidoc -A "Alyssa Quek" -f -F -o docs facemorpher/

cd docs
# Append module path to end of conf file
echo "sys.path.insert(0, os.path.abspath('../'))" >> conf.py
# Make sphinx documentation
make html
cd ..