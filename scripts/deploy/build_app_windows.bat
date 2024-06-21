
set CONDA_DIR=%cd%\conda
set PYTHON_VERSION=3.8

for /F %%i in ('git rev-parse --short HEAD') do set GIT_COMMIT_SHORT=%%i

call conda create -y -n pyrpl python=%PYTHON_VERSION%
call conda activate pyrpl
call conda install -y numpy=1.19 pyqtgraph=0.12 pandas=1.3 scipy paramiko nose pip pyqt qtpy=1.9.0 pyyaml ipywidgets notebook
pip uninstall -y pyopenssl cryptography
pip install -U pyopenssl==22.0.0 cryptography==36.0.2
pip install -U coverage scp quamash
pip install -U matplotlib==3.6 Pillow pyparsing cycler kiwisolver
pip install pyinstaller
pip install PyQt5

cd ..\..

python setup.py develop

pyinstaller pyrpl.spec

xcopy /f .\dist\pyrpl.exe .\pyrpl-%GIT_COMMIT_SHORT%.exe