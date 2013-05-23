Mobile Launch Platform
======================

A portable (cross-platform) EVE Online launcher


Features
--------
- Remember last-used eve install dir
- Remember last-used singularity install dir
- Remember usernames
- Launch multiple alts at once


Setup
-----
```
virtualenv venv
./venv/bin/pip install -e ./
```

Run
---
```
With a specific eve install:
	./venv/bin/eve-mlp --evedir /home/bob/Games/EVE

Launch multiple alts at once:
	./venv/bin/eve-mlp --username Bob --username Fred

Launch the last-used eve install with the last-used usernames:
    ./venv/bin/eve-mlp
```

Shameless Plug
--------------
Send ISK to Shish Tukay if you want to encourage more work on this :)


TODO
----
- pointy-clicky GUI, with functionality over fashion
- remember password(s)?
  - Have one master password to unlock passwords for all alts
- nicer installation (install into $PATH)
- download & apply patches?


Thanks
------
Made using Artefact2's PHP launcher as a reference:

https://github.com/Artefact2/eve-launcher

