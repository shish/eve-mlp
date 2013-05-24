#!/bin/bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/
../pyinstaller-2.0/pyinstaller.py --onefile --icon icon.ico --name eve-mlp eve_mlp/main_cli.py
../pyinstaller-2.0/pyinstaller.py --onefile --icon icon.ico --name eve-gmlp eve_mlp/main_gui.py --windowed --resource icon.ico --resource LICENSE.txt
