#!/bin/bash

CONDA_DIR="/opt/conda"
PYTHON_VERSION="3.8"
GIT_COMMIT_SHORT=$(git rev-parse --short HEAD)
DATE=$(date +%Y-%m)
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda.sh
chmod +x Miniconda.sh
./Miniconda.sh -u -b -p $CONDA_DIR
$CONDA_DIR/bin/conda create -y -n pyrpl python=$PYTHON_VERSION
# eval "$($CONDA_DIR/bin/conda shell.bash hook)"
source $CONDA_DIR/bin/activate pyrpl
$CONDA_DIR/bin/conda install -y numpy=1.19 pyqtgraph=0.12 pandas=1.3 scipy paramiko nose pip pyqt qtpy=1.9.0 pyyaml ipywidgets notebook
pip uninstall -y pyopenssl cryptography
pip install -U pyopenssl==22.0.0 cryptography==36.0.2
pip install -U coverage scp quamash
pip install -U matplotlib==3.6 Pillow pyparsing cycler kiwisolver
pip install pyinstaller
cd ../..

python setup.py develop

# make package
pyinstaller pyrpl.spec
cp ./dist/pyrpl ./pyrpl-$DATE-$GIT_COMMIT_SHORT
zip pyrpl-linux_x86-$DATE-$GIT_COMMIT_SHORT.zip pyrpl-$DATE-$GIT_COMMIT_SHORT

# run tests
# export REDPITAYA_HOSTNAME=200.0.0.29
# nosetests

# run app
# Note: disable rm command in end of script
# python -m pyrpl

rm -rf $CONDA_DIR ./scripts/deploy/Miniconda.sh