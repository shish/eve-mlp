@echo off

REM For people who don't have python in their path, assume it exists in the default location as a fallback
SET PATH=%PATH%;C:\Python27

python.exe ..\pyinstaller-2.0\pyinstaller.py compile_generic.spec

pause
