
for /F %%i in ('git rev-parse --short HEAD') do set GIT_COMMIT_SHORT=%%i
set LINUX_VER="3.00"

call conda env create -f ..\..\environment_pyrpl_windows.yml
call conda activate pyrpl-env

cd ..\..

python setup.py develop

pyinstaller pyrpl.spec

xcopy /Y .\dist\pyrpl.exe .\pyrpl-windows-%LINUX_VER%-%GIT_COMMIT_SHORT%.exe 