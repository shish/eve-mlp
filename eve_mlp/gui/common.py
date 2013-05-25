import os
import sys
import wx


def resource(path):
    """
    Given that X was in our folder in development, where could it be now?

    - PyInstaller one-dir mode: in the same folder as the .exe
    - One-file mode: in a temporary unpacking folder
    - We're still in development: the current folder
    - We're on a mac: a couple of folders up from the binary

    Try all of those, return the first file path that exists
    """
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
    """
    wx doesn't automatically load all the different sizes from a .ico :(
    """
    icons = wx.IconBundle()
    for sz in [16, 32, 48]:
        try:
            icon = wx.Icon(fn, wx.BITMAP_TYPE_ICO, desiredWidth=sz, desiredHeight=sz)
            icons.AddIcon(icon)
        except:
            pass
    return icons


def get_password(parent, title):
    """
    These four lines appeared several times in places where having a single
    function call would have been much more convenient; so at the cost of a
    little flexibility, this makes things tidier.
    """
    ped = wx.PasswordEntryDialog(parent, title)
    ped.ShowModal()
    pw = ped.GetValue()
    ped.Destroy()
    return pw
