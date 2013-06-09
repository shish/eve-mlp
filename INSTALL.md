
Setup
-----
```
$ sudo apt-get install python-requests python-wxgtk2.8    # debian / ubuntu
$ sudo yum install python-requests wxPython               # red hat / fedora / centos

$ sudo pip install -e ./                                  # install eve-mlp / eve-gmlp commands
$ ./main_gui.py                                           # or run straight from the source folder
```

Building Binaries
-----------------
Requires `python` and `git` commands in the path, and pyinstaller in ../pyinstaller-2.0/,
as well as the python module dependencies from the app itself.

Though TBH, if you can be bothered to set up a large dev environment with extras for .exe
building, you might as well just set up a small dev environment and run from source...

