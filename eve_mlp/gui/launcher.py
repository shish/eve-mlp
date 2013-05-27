import wx
import wx.grid

from eve_mlp.gui.chargrid import CharGrid


class LauncherPanel(wx.Panel):
    """
    List all the known LaunchConfig objects, so the player can pick and interact with them

    Now that settings are a separate panel, it might make sense to move away from
    a spreadsheet view?
    """

    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.config = config
        self.main = parent

        box = wx.StaticBoxSizer(wx.StaticBox(self, label="Character List"), wx.VERTICAL)

        char_list = CharGrid(self, self.main)

        #launch_all = wx.Button(self, -1, "Launch All")
        #self.Bind(wx.EVT_BUTTON, self.OnLaunchAll, launch_all)

        launch_sel = wx.Button(self, -1, "Launch Selected")
        self.Bind(wx.EVT_BUTTON, self.OnLaunchSel, launch_sel)

        box.Add(char_list, 1)
        #box.Add(launch_all, 0, wx.EXPAND)
        box.Add(launch_sel, 0, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()

    def OnLaunchAll(self, evt):
        for launch_config in self.config.launches:
            self.main.launch(launch_config)

    def OnLaunchSel(self, evt):
        for launch_config in self.config.launches:
            if launch_config.selected:
                self.main.launch(launch_config)
