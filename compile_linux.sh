#!/bin/bash
export VERSION=`git describe | sed s/v//`
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/
../pyinstaller-2.0/pyinstaller.py --onefile --icon icon.ico --name eve-mlp main_cli.py
../pyinstaller-2.0/pyinstaller.py --onefile --icon icon.ico --name eve-gmlp main_gui.py --windowed --resource icon.ico --resource LICENSE.txt --resource help.html

cd dist
cp ../LICENSE.txt ../icon.ico ../help.html ./
tar cvzf eve-mlp-$VERSION.tar.gz eve-mlp LICENSE.txt
tar cvzf eve-gmlp-$VERSION.tar.gz eve-gmlp LICENSE.txt icon.ico help.html
