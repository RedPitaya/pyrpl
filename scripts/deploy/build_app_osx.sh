#!/bin/bash

CONDA_DIR=$(pwd)/conda
GIT_COMMIT_SHORT=$(git rev-parse --short HEAD)
LINUX_VER="3.00"
DATE=$(date +%Y-%m)
wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-arm64.sh -O Miniconda.sh
chmod +x Miniconda.sh
./Miniconda.sh -u -b -p $CONDA_DIR

$CONDA_DIR/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
$CONDA_DIR/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
$CONDA_DIR/bin/conda env create -f ../../environment_pyrpl_osx.yml
source $CONDA_DIR/bin/activate pyrpl-env

cd ../..

python setup.py develop

# make package
pyinstaller pyrpl.spec
cp ./dist/pyrpl ./pyrpl-$DATE-$LINUX_VER-$GIT_COMMIT_SHORT
zip pyrpl-osx-arm64-$DATE-$LINUX_VER-$GIT_COMMIT_SHORT.zip pyrpl-$DATE-$LINUX_VER-$GIT_COMMIT_SHORT

# run tests
# export REDPITAYA_HOSTNAME=200.0.0.29
# nosetests

# run app
# Note: disable rm command in end of script
# python -m pyrpl

rm -rf $CONDA_DIR ./scripts/deploy/Miniconda.sh