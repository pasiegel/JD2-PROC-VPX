@echo off
REM Registers the VPROC.Controller COM server so VPX can launch the P-ROC game.
REM Run this once after installation, or any time the paths change.
REM Must be run as Administrator.

cd /d C:\P-ROC\tools
C:\Python27\python.exe register_vpcom.py --register
if %ERRORLEVEL% == 0 (
    echo COM server registered successfully.
) else (
    echo ERROR: Registration failed. Try running as Administrator.
)
pause
