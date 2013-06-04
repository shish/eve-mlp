#!/bin/bash
export VERSION=`git describe | sed s/v//`
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/
../pyinstaller-2.0/pyinstaller.py compile_generic.spec

cd dist
tar cvzf eve-mlp-$VERSION.tar.gz eve-mlp
tar cvzf eve-gmlp-$VERSION.tar.gz eve-gmlp
