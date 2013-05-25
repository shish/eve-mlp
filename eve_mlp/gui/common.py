import os
import sys
import wx

   
def resource(path):
    ideas = [
        os.path.join(os.path.dirname(sys.argv[0]), path),
        os.path.join(os.environ.get("_MEIPASS2", "/"), path),
        path,
    ]
    for n in range(0, 5):
        parts = ([".."] * n + [path])
        ideas.append(os.path.join(*parts))
    for p in ideas:
        if os.path.exists(p):
            return p
    return None


def icon_bundle(fn):
    icons = wx.IconBundle() 
    for sz in [16, 32, 48]: 
        try: 
            icon = wx.Icon(fn, wx.BITMAP_TYPE_ICO, desiredWidth=sz, desiredHeight=sz) 
            icons.AddIcon(icon) 
        except: 
            pass
    return icons


def get_password(parent, title):
    ped = wx.PasswordEntryDialog(parent, title)
    ped.ShowModal()
    pw = ped.GetValue()
    ped.Destroy()
    return pw
