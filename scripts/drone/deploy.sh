#!/bin/bash

pushd /var/cache/drone/src/github.com/kaedroho/wagtail

python3 setup.py sdist
python3 setup.py bdist_wheel
python2 setup.py bdist_wheel

popd
