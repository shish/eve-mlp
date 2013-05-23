Mobile Launch Platform
======================

A portable (cross-platform) EVE Online launcher


Features
--------
- Remember usernames
- Remember passwords (one master password for several alts)
- Launch multiple alts at once


Setup
-----
```
virtualenv venv
./venv/bin/pip install -e ./
sudo ln -s `pwd`/venv/bin/eve-mlp /usr/local/bin
```

Run
---
```
With a specific eve install:
	eve-mlp --evedir /home/bob/Games/EVE

Launch multiple alts at once:
	eve-mlp --username Bob --username Fred --username Jim --username Dave

Launch the last-used eve install with the last-used usernames:
    eve-mlp

Store the passwords for known usernames, but don't actually launch eve:
    eve-mlp --save-passwords --dry

Launch all of your alts in one go, only needing to enter one master password:
    eve-mlp

```

Shameless Plug
--------------
Send ISK to Shish Tukay if you want to encourage more work on this :)


TODO
----
- pointy-clicky GUI, with functionality over fashion
- download & apply patches?
- windows port


Thanks
------
Artefact2, for his proof-of-concept PHP launcher:

https://github.com/Artefact2/eve-launcher

Josh Davis & Alex Martelli for SlowAES, a pure-python AES implementation:

https://code.google.com/p/slowaes/

CCP, for making the best virtual universe, and for not sending their lawyers after me ( please ;) )
