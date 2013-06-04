Mobile Launch Platform
======================

A portable (cross-platform) EVE Online launcher

Screenshots & binary downloads: http://code.shishnet.org/eve-mlp/

Features
--------
- Remember usernames
- Remember passwords (one master password for several alts)
- Launch multiple alts at once
  - Different Eve folders for each of them, if you want to keep settings and cache separate
- Systray icon
  - Double click to hide main window
  - Right click -> launch character

Setup
-----
```
$ sudo apt-get install python-requests python-wxgtk2.8    # debian / ubuntu
$ sudo yum install python-requests wxPython               # red hat / fedora / centos

$ sudo pip install -e ./                                  # install eve-mlp / eve-gmlp commands
$ ./main_gui.py                                           # or run straight from the source folder
```

Run
---
```
Run the gui:
    eve-gmlp
    
Set the default game path:
    eve-mlp --gamepath /home/bob/Games/EVE

Add a new launch configuration with given username and custom path:
    eve-mlp --config MyConfig --username Fred --gamepath /home/fred/Games/EVE

Update the new config to be run by default (ie, if no configs are explicitly selected):
    eve-mlp --config MyConfig --selected

Launch multiple alts at once:
    eve-mlp --launch MyConfig --launch CynoAlt-Screen2 --launch MarketAlt-LowGraphics

Launch all of your selected alts in one go:
    eve-mlp
```

Building Binaries
-----------------
Requires `python` and `git` commands in the path, and pyinstaller in ../pyinstaller-2.0/,
as well as the python module dependencies from the app itself.

Though TBH, if you can be bothered to set up a large dev environment with extras for .exe
building, you might as well just set up a small dev environment and run from source...

Shameless Plug
--------------
Send ISK to Shish Tukay if you want to encourage more work on this :)

Thanks
------
Artefact2, for his proof-of-concept PHP launcher: https://github.com/Artefact2/eve-launcher

CCP, for making the best virtual universe, and for not sending their lawyers after me ( please ;) )
