
set CONDA_DIR=%cd%\conda

for /F %%i in ('git rev-parse --short HEAD') do set GIT_COMMIT_SHORT=%%i
set LINUX_VER="3.00"
set YEAR=%date:~-4%
set MONTH=%date:~3,2%
set DATE=%YEAR%-%MONTH%
call conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
call conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

call conda env create -f ..\..\environment_uni_pyrpl.yml
call conda activate pyrpl-env

cd ..\..

python setup.py develop

pyinstaller pyrpl.spec

xcopy /f .\dist\pyrpl.exe .\pyrpl-windows-%DATE-%LINUX_VER-%GIT_COMMIT_SHORT%.exe