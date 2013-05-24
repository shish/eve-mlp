Mobile Launch Platform
======================

A portable (cross-platform) EVE Online launcher


Features
--------
- Remember usernames
- Remember passwords (one master password for several alts)
- Launch multiple alts at once
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
Command line with a specific eve install:
	eve-mlp --eve-dir /home/bob/Games/EVE

Launch multiple alts at once:
	eve-mlp --username Bob --username Fred --username Jim --username Dave

Launch the last-used eve install with the last-used usernames:
    eve-mlp

Store the passwords for known usernames, but don't actually launch eve:
    eve-mlp --save-passwords --dry

Launch all of your alts in one go, only needing to enter one master password:
    eve-mlp

Run the gui:
	eve-gmlp
```

Shameless Plug
--------------
Send ISK to Shish Tukay if you want to encourage more work on this :)


TODO
----
- download & apply patches?
  - at least detect the currently installed and currently live versions, launch the official patcher if there's a patch to have
- wine flags management / dll overrides / etc (though it actually all works out of the box for me...)
- unit tests


Thanks
------
Artefact2, for his proof-of-concept PHP launcher:

https://github.com/Artefact2/eve-launcher

Josh Davis & Alex Martelli for SlowAES, a pure-python AES implementation:

https://code.google.com/p/slowaes/

CCP, for making the best virtual universe, and for not sending their lawyers after me ( please ;) )
