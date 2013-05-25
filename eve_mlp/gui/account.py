import wx

class AccountPanel(wx.Panel):
    def __init__(self, parent, default=False):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.default = default

        self.box_label = wx.StaticBox(self, label="Default Settings")
        box = wx.StaticBoxSizer(self.box_label, wx.VERTICAL)
        grid = wx.GridSizer(0, 2, 2, 2)

        if not default:
            grid.Add(wx.StaticText(self, wx.ID_ANY, "Setup Name"), 0, wx.EXPAND)
            self.confname = wx.TextCtrl(self)
            def set_confname(evt):
                if self.confname.GetLabel():
                    self.account.confname = self.confname.GetLabel()
            self.Bind(wx.EVT_TEXT, set_confname, self.confname)
            grid.Add(self.confname, 1, wx.EXPAND)

            grid.Add(wx.StaticText(self, wx.ID_ANY, "Username"), 0, wx.EXPAND)
            self.username = wx.TextCtrl(self)
            def set_username(evt):
                self.account.username = self.username.GetLabel() or None
            self.Bind(wx.EVT_TEXT, set_username, self.username)
            grid.Add(self.username, 1, wx.EXPAND)

            grid.Add(wx.StaticText(self, wx.ID_ANY, "Password"), 0, wx.EXPAND)
            self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD)
            def set_password(evt):
                self.account.password = self.password.GetLabel() or None
            self.Bind(wx.EVT_TEXT, set_password, self.password)
            grid.Add(self.password, 1, wx.EXPAND)

        grid.Add(wx.StaticText(self, wx.ID_ANY, "Game Path"), 0, wx.EXPAND)
        self.gamepath = wx.Button(self, label="")
        def set_gamepath(evt):
            dd = wx.DirDialog(self, "Pick a game folder", self.account.gamepath)
            if dd.ShowModal() == wx.ID_OK:
                self.account.gamepath = dd.GetPath()
                self.gamepath.SetLabel(self.account.gamepath)
            else:
                self.account.gamepath = None
                self.gamepath.SetLabel("(Default)")
            dd.Destroy()
        self.Bind(wx.EVT_BUTTON, set_gamepath, self.gamepath)
        grid.Add(self.gamepath, 1, wx.EXPAND)

        grid.Add(wx.StaticText(self, wx.ID_ANY, "Server"), 0, wx.EXPAND)
        self.serverid = wx.ComboBox(self, choices=["(Default)", "Tranquility", "Singularity"], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        def set_serverid(evt):
            s = self.serverid.GetValue()
            if s == "(Default)":
                self.account.serverid = None
            else:
                self.account.serverid = s.lower()
        self.serverid.Bind(wx.EVT_COMBOBOX, set_serverid, self.serverid)
        grid.Add(self.serverid, 1, wx.EXPAND)
        
        box.Add(grid, 1, wx.EXPAND)
        self.SetSizer(box)
        self.Layout()

    def set_account(self, account):
        self.account = account
        
        self.box_label.SetLabel("%s's settings" % account.confname if account.confname else "Default Settings")
        if not self.default:
            self.confname.SetLabel(account.confname or "")
            self.username.SetLabel(account.username or "")
            self.password.SetLabel(account.password or "")
        self.gamepath.SetLabel(account._gamepath or "(Default)")

        if account._serverid == "tranquility":
            self.serverid.Select(1)
        elif account._serverid == "singularity":
            self.serverid.Select(2)
        else:
            self.serverid.Select(0)
