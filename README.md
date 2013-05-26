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

$ sudo pip install -e ./
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

Shameless Plug
--------------
Send ISK to Shish Tukay if you want to encourage more work on this :)


Thanks
------
Artefact2, for his proof-of-concept PHP launcher:

https://github.com/Artefact2/eve-launcher

Josh Davis & Alex Martelli for SlowAES, a pure-python AES implementation:

https://code.google.com/p/slowaes/

CCP, for making the best virtual universe, and for not sending their lawyers after me ( please ;) )
