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

        # box = wx.StaticBoxSizer(wx.StaticBox(self, label="Launch Configurations"), wx.VERTICAL)
        box = wx.BoxSizer(wx.VERTICAL)
        box.SetMinSize((250, 200))

        self.char_list = ulc.UltimateListCtrl(
            self,
            agwStyle=
                wx.LC_REPORT
                | wx.LC_HRULES
                | ulc.ULC_NO_HEADER
                | ulc.ULC_HAS_VARIABLE_ROW_HEIGHT
        )
        self.char_list.InsertColumn(0, "")
        self.char_list.InsertColumn(1, "Config Name")
        self.char_list.InsertColumn(2, "")

        #launch_all = wx.Button(self, -1, "Launch All")
        launch_sel = wx.Button(self, -1, "Launch Ticked")
        add_setup = wx.Button(self, -1, "Add Setup")
        del_setup = wx.Button(self, -1, "Remove Setup")

        self.Bind(ulc.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.char_list)
        #self.Bind(wx.EVT_BUTTON, self.OnLaunchAll, launch_all)
        self.Bind(wx.EVT_BUTTON, self.OnLaunchSel, launch_sel)
        self.Bind(wx.EVT_BUTTON, self.OnAddSetup, add_setup)
        self.Bind(wx.EVT_BUTTON, self.OnDelSetup, del_setup)

        box.Add(self.char_list, 1, wx.EXPAND)
        #box.Add(launch_all, 0, wx.EXPAND)
        box.Add(launch_sel, 0, wx.EXPAND)
        box.Add(add_setup, 0, wx.EXPAND)
        box.Add(del_setup, 0, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()

        self.update()

    def update(self):
        self.char_list.DeleteAllItems()

        for n, lc in enumerate(self.config.launches):
            self.char_list.Append(["", lc.confname, ""])

            item = self.char_list.GetItem(n, 0)
            check = wx.CheckBox(self.char_list, 4000 + n)
            check.SetValue(lc.selected)
            self.Bind(wx.EVT_CHECKBOX, self.OnCheck, check)
            item.SetWindow(check)
            self.char_list.SetItem(item)

            item = self.char_list.GetItem(n, 2)
            button = wx.Button(self.char_list, 4000 + n, label="Launch")
            self.Bind(wx.EVT_BUTTON, self.OnLaunch, button)
            item.SetWindow(button)
            self.char_list.SetItem(item)

        self.char_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.char_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.char_list.SetColumnWidth(2, wx.LIST_AUTOSIZE)

    def OnCheck(self, evt):
        uid = evt.GetId() - 4000
        self.config.launches[uid].selected = evt.IsChecked()

    def OnLaunch(self, evt):
        uid = evt.GetId() - 4000
        self.main.launch(self.config.launches[uid])

    def OnItemSelected(self, evt):
        self.main.OnLaunchConfigSelected(evt.m_itemIndex)

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
        uid = self.char_list.GetNextItem(-1, state=wx.LIST_STATE_SELECTED)
        if uid >= 0:
            del self.config.launches[uid]
            self.update()
            self.main.OnLaunchConfigSelected(0)
