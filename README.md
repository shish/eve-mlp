Mobile Launch Platform
======================

A portable (cross-platform) EVE Online launcher


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
```

Shameless Plug
--------------
Send ISK to Shish Tukay if you want to encourage more work on this :)

TODO
----
- pointy-clicky GUI, with functionality over fashion
- have --evedir use the last-used dir as default
- remember username(s)
- remember password(s)?
  - Have one master password to unlock passwords for all alts
- nicer installation (install into $PATH)
- download & apply patches?

Thanks
------
Made using Artefact2's PHP launcher as a reference:

https://github.com/Artefact2/eve-launcher

