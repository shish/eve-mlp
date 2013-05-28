import wx
import wx.grid

from eve_mlp.common import LaunchConfig
import wx.lib.agw.ultimatelistctrl as ulc


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

        self.selected_id = 0

        # box = wx.StaticBoxSizer(wx.StaticBox(self, label="Launch Configurations"), wx.VERTICAL)
        box = wx.BoxSizer(wx.VERTICAL)
        box.SetMinSize((250, 200))

        self.lc_grid = wx.FlexGridSizer(0, 3)
        self.lc_grid.AddGrowableCol(1)

        #launch_all = wx.Button(self, -1, "Launch All")
        launch_sel = wx.Button(self, -1, "Launch Ticked")
        add_setup = wx.Button(self, -1, "Add Setup")
        del_setup = wx.Button(self, -1, "Remove Setup")

        #self.Bind(ulc.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.char_list)
        #self.Bind(wx.EVT_BUTTON, self.OnLaunchAll, launch_all)
        self.Bind(wx.EVT_BUTTON, self.OnLaunchSel, launch_sel)
        self.Bind(wx.EVT_BUTTON, self.OnAddSetup, add_setup)
        self.Bind(wx.EVT_BUTTON, self.OnDelSetup, del_setup)

        box.Add(self.lc_grid, 1, wx.EXPAND)
        #box.Add(launch_all, 0, wx.EXPAND)
        box.Add(launch_sel, 0, wx.EXPAND)
        box.Add(add_setup, 0, wx.EXPAND)
        box.Add(del_setup, 0, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()

        self.update()

    def update(self):
        self.lc_grid.Clear(True)

        for n, lc in enumerate(self.config.launches):
            check = wx.CheckBox(self, 4000 + n)
            check.SetValue(lc.selected)
            self.Bind(wx.EVT_CHECKBOX, self.OnCheck, check)
            self.lc_grid.Add(check, 0, wx.ALIGN_CENTER_VERTICAL)

            name = wx.Button(self, 4100 + n, lc.confname, style=wx.NO_BORDER|wx.BU_LEFT)
            if n == self.selected_id:
                f = name.GetFont()
                name.SetFont(wx.Font(f.GetPointSize(), f.GetFamily(), f.GetStyle(), wx.BOLD))
            self.Bind(wx.EVT_BUTTON, self.OnItemSelected, name)
            self.lc_grid.Add(name, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)

            button = wx.Button(self, 4200 + n, label="Launch")
            self.Bind(wx.EVT_BUTTON, self.OnLaunch, button)
            self.lc_grid.Add(button)

        self.Layout()

    def OnCheck(self, evt):
        uid = evt.GetId() - 4000
        self.config.launches[uid].selected = evt.IsChecked()

    def OnItemSelected(self, evt):
        uid = evt.GetId() - 4100
        self.main.OnLaunchConfigSelected(uid)
        self.selected_id = uid
        self.update()

    def OnLaunch(self, evt):
        uid = evt.GetId() - 4200
        self.main.launch(self.config.launches[uid])

    def OnLaunchAll(self, evt):
        for launch_config in self.config.launches:
            self.main.launch(launch_config)

    def OnLaunchSel(self, evt):
        for launch_config in self.config.launches:
            if launch_config.selected:
                self.main.launch(launch_config)

    def OnAddSetup(self, evt):
        self.config.launches.append(LaunchConfig(self.config.defaults, {"confname": "New Setup"}))
        self.main.OnLaunchConfigSelected(len(self.config.launches) - 1)
        self.update()

    def OnDelSetup(self, evt):
        del self.config.launches[self.selected_id]
        if len(self.config.launches) == 0:  # don't allow the config list to be totally empty
            self.config.launches.append(LaunchConfig(self.config.defaults, {"confname": "New Setup"}))
        self.selected_id = 0
        self.main.OnLaunchConfigSelected(0)
        self.update()
