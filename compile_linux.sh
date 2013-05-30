#!/bin/bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/
../pyinstaller-2.0/pyinstaller.py --onefile --icon icon.ico --name eve-mlp main_cli.py
../pyinstaller-2.0/pyinstaller.py --onefile --icon icon.ico --name eve-gmlp main_gui.py --windowed --resource icon.ico --resource LICENSE.txt --resource help.html
