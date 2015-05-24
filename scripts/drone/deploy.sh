#!/bin/bash

pushd /var/cache/drone/src/github.com/kaedroho/wagtail

echo "Building packages..."

# Install NPM dependencies for building SASS
npm install > /dev/null

# Create sdist
python3 setup.py sdist > /dev/null

# Create wheel for Python 3
pip3 install wheel
python3 setup.py bdist_wheel > /dev/null

# Create wheel for Python 2
pip2 install wheel
python2 setup.py bdist_wheel > /dev/null

# TODO Upload!

popd
