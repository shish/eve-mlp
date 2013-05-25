@echo off

REM For people who don't have python in their path, assume it exists in the default location as a fallback
SET PATH=%PATH%;C:\Python27

python.exe ..\pyinstaller-2.0\pyinstaller.py --onefile --icon icon.ico --name eve-mlp eve_mlp/main_cli.py
python.exe ..\pyinstaller-2.0\pyinstaller.py --onefile --icon icon.ico --name eve-gmlp eve_mlp/main_gui.py --windowed --resource icon.ico --resource LICENSE.txt

pause
