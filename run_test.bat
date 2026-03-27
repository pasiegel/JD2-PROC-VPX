@echo off
set PYTHONPATH=C:\P-ROC\games\JD2;C:\P-ROC\pyprocgame;C:\Python27\DLLs;C:\Python27\lib;C:\Python27;C:\Python27\lib\site-packages;C:\Python27\lib\site-packages\win32;C:\Python27\lib\site-packages\win32\lib;C:\Python27\lib\site-packages\Pythonwin
cd /d C:\P-ROC\games\JD2
C:\Python27\python.exe -c "import ast; ast.parse(open('jd2.py').read()); print 'jd2.py syntax OK'"
C:\Python27\python.exe -c "import sys; sys.path.insert(0,'C:\\P-ROC\\games\\JD2'); sys.path.insert(0,'C:\\P-ROC\\pyprocgame'); from procgame.game import BasicGame; print 'pyprocgame BasicGame: OK'"
C:\Python27\python.exe -c "import sys; sys.path.insert(0,'C:\\P-ROC\\games\\JD2'); sys.path.insert(0,'C:\\P-ROC\\pyprocgame'); import pinproc; print 'pinproc: OK'"
