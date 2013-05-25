import wx

from eve_mlp.gui.common import resource, icon_bundle


class TrayIcon(wx.TaskBarIcon):
    def __init__(self, main):
        wx.TaskBarIcon.__init__(self)
        self.main = main
        self.config = main.config
        self.SetIcon(wx.Icon(resource("icon.ico"), wx.BITMAP_TYPE_ICO, desiredWidth=16, desiredHeight=16), "Mobile Launcher Platform")
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnLeftDClick)
        self.CreateMenu()

    def CreateMenu(self):
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnPopup)
        self.menu = wx.Menu()

        for n, launch_config in enumerate(self.config.launches):
            m_launch = self.menu.Append(3000 + n, 'Launch ' + launch_config.confname)
            self.Bind(wx.EVT_MENU, self.OnLaunch, m_launch)

        self.menu.AppendSeparator()
        m_launch_all = self.menu.Append(3200, 'Launch All')
        self.Bind(wx.EVT_MENU, self.OnLaunch, m_launch_all)

        self.menu.AppendSeparator()
        m_exit = self.menu.Append(wx.ID_EXIT, 'E&xit')
        self.Bind(wx.EVT_MENU, self.main.OnClose, m_exit)

    def OnPopup(self, event):
        self.CreateMenu()  # refresh with latest usernames
        self.PopupMenu(self.menu)

    def OnLeftDClick(self, evt):
        if self.main.IsShown():
            self.main.Hide()
        else:
            self.main.Show()

    def OnLaunch(self, evt):
        uid = evt.GetId() - 3000
        if uid == 200:
            for launch_config in self.config.launches:
                self.main.launch(launch_config)
        else:
            self.main.launch(self.config.launches[uid])
