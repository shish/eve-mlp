import wx
import logging


log = logging.getLogger(__name__)


def ltrim(x):
    """
    Trim a folder name so that it fits on a button, eg:

      /home/media/Games/CCP/Eve -> ...ames/CCP/Eve

    This could probably be done better:
      - split at folder boundaries if possible
      - show some from the start and some from the end

      /home/.../CCP/Eve
    """
    if not x:
        return "(Default)"
    elif len(x) > 20:
        return "..." + x[-20:]
    else:
        return x


class LaunchConfigPanel(wx.Panel):
    """
    A GUI for editing an individual LaunchConfig object.

    If default=True, it will only show the fields that make sense
    when default'ed (eg game install folder is often shared between
    launches, but account names are largely unique)
    """

    def __init__(self, parent, default=False):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.default = default

        self.box_label = wx.StaticBox(self, label="Default Settings")
        box = wx.StaticBoxSizer(self.box_label, wx.VERTICAL)
        grid = wx.FlexGridSizer(0, 2, 2, 2)
        grid.AddGrowableCol(1)

        if not default:
            grid.Add(wx.StaticText(self, wx.ID_ANY, "Setup Name"), 0, wx.ALIGN_CENTER_VERTICAL)
            self.confname = wx.TextCtrl(self)
            def set_confname(evt):
                if self.confname.GetLabel():
                    self.launch_config.confname = self.confname.GetValue()
            self.Bind(wx.EVT_TEXT, set_confname, self.confname)
            grid.Add(self.confname, 1, wx.EXPAND)

            grid.Add(wx.StaticText(self, wx.ID_ANY, "Username"), 0, wx.ALIGN_CENTER_VERTICAL)
            self.username = wx.TextCtrl(self)
            def set_username(evt):
                self.launch_config.username = self.username.GetValue() or None
            self.Bind(wx.EVT_TEXT, set_username, self.username)
            grid.Add(self.username, 1, wx.EXPAND)

            grid.Add(wx.StaticText(self, wx.ID_ANY, "Password"), 0, wx.ALIGN_CENTER_VERTICAL)
            self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD)
            def set_password(evt):
                self.launch_config.password = self.password.GetValue() or None
            self.Bind(wx.EVT_TEXT, set_password, self.password)
            grid.Add(self.password, 1, wx.EXPAND)

            grid.Add(wx.StaticText(self, wx.ID_ANY, "Selected"), 0, wx.ALIGN_CENTER_VERTICAL)
            self.selected = wx.CheckBox(self)
            def set_selected(evt):
                self.launch_config.selected = self.selected.IsChecked()
            self.Bind(wx.EVT_CHECKBOX, set_selected, self.selected)
            grid.Add(self.selected, 1, wx.EXPAND)

        grid.Add(wx.StaticText(self, wx.ID_ANY, "Game Path"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.gamepath = wx.Button(self, label="")
        def set_gamepath(evt):
            dd = wx.DirDialog(self, "Pick a game folder", self.launch_config.gamepath or ".")
            if dd.ShowModal() == wx.ID_OK:
                self.launch_config.gamepath = dd.GetPath()
                self.gamepath.SetLabel(self.launch_config.gamepath[-20:])
            else:
                self.launch_config.gamepath = None
                self.gamepath.SetLabel("(Default)")
            dd.Destroy()
        self.Bind(wx.EVT_BUTTON, set_gamepath, self.gamepath)
        grid.Add(self.gamepath, 1, wx.EXPAND)

        grid.Add(wx.StaticText(self, wx.ID_ANY, "Server"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.serverid = wx.ComboBox(self, choices=["(Default)", "Tranquility", "Singularity"], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        def set_serverid(evt):
            s = self.serverid.GetValue()
            if s == "(Default)":
                self.launch_config.serverid = None
            else:
                self.launch_config.serverid = s.lower()
        self.serverid.Bind(wx.EVT_COMBOBOX, set_serverid, self.serverid)
        grid.Add(self.serverid, 1, wx.EXPAND)

        box.Add(grid, 1, wx.EXPAND)
        self.SetSizer(box)
        self.Layout()

    def set_launch_config(self, launch_config):
        self.launch_config = launch_config

        log.info("Setting launch_config editor to use %s", launch_config)

        self.box_label.SetLabel("%s's settings" % launch_config.confname if launch_config.confname else "Default Settings")
        if not self.default:
            self.confname.SetValue(launch_config.confname or "")
            self.username.SetValue(launch_config.username or "")
            self.password.SetValue(launch_config.password or "")
            self.selected.SetValue(launch_config.selected or False)
        self.gamepath.SetLabel(ltrim(launch_config._gamepath))

        if launch_config._serverid == "tranquility":
            self.serverid.Select(1)
        elif launch_config._serverid == "singularity":
            self.serverid.Select(2)
        else:
            self.serverid.Select(0)
