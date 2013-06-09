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

Run
---
```
Run the gui:
    eve-gmlp
    
Set the default game path:
    eve-mlp config --gamepath /home/bob/Games/EVE

Add a new launch configuration:
    eve-mlp add MyConfig

Set username and custom path:
    eve-mlp config MyConfig --username Fred --gamepath /home/fred/Games/EVE

Show all the known launch configurations:
    eve-mlp list

Launch multiple alts at once:
    eve-mlp launch MyConfig CynoAlt-Screen2 MarketAlt-LowGraphics

Launch all of your selected alts in one go:
    eve-mlp launch
```

Shameless Plug
--------------
Send ISK to Shish Tukay if you want to encourage more work on this :)

Thanks
------
Artefact2, for his proof-of-concept PHP launcher: https://github.com/Artefact2/eve-launcher

CCP, for making the best virtual universe, and for not sending their lawyers after me ( please ;) )
