import sys
import logging

import wx
from wx.lib.mixins.inspection import InspectableApp

from eve_mlp.common import *


log = logging.getLogger(__name__)


class LauncherPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        box = wx.StaticBoxSizer(wx.StaticBox(self, label="Character List"), wx.VERTICAL)

        clist = wx.StaticText(self, -1, "Character list goes here")
        launch_all = wx.Button(self, -1, "Launch All")

        box.Add(clist, 1)
        box.Add(launch_all, 0)

        self.SetSizer(box)
        self.Layout()

class MainFrame(wx.Frame):
    def __menu(self):
        menu_bar = wx.MenuBar()

        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menu_bar.Append(menu, "&File")

        menu = wx.Menu()
        m_tranq = menu.Append(wx.ID_EXIT, "Tranquility (Main)", "", kind=wx.ITEM_RADIO)
        m_singu = menu.Append(wx.ID_EXIT, "Singularity (Beta)", "", kind=wx.ITEM_RADIO)
        #self.Bind(wx.EVT_MENU, self.OnClose, m_tranq)
        #self.Bind(wx.EVT_MENU, self.OnClose, m_singu)
        menu_bar.Append(menu, "&Server")

        menu = wx.Menu()
        m_rempasswd = menu.Append(wx.ID_EXIT, "Remember Passwords", "", kind=wx.ITEM_CHECK)
        m_loc_tranq = menu.Append(wx.ID_EXIT, "Locate Eve Install", "")
        m_loc_singu = menu.Append(wx.ID_EXIT, "Locate Singularity Install", "")
        #self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menu_bar.Append(menu, "&Options")

        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "Launch Patcher", "")
        m_exit = menu.Append(wx.ID_EXIT, "Launch Repair", "")
        #self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        #menu_bar.Append(menu, "&Tools")

        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        #self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menu_bar.Append(menu, "&Help")

        return menu_bar

    def __init_gui(self, parent):
        wx.Frame.__init__(self, parent, -1, "Mobile Launch Platform", size=(640, 480))
        self.Bind(wx.EVT_CLOSE, self.OnWinClose)

        self.SetMenuBar(self.__menu())

        #self.filterSettings = FilterSettings(self)
        #self.grid = LogEntryGrid(self, log)
        #self.filterList = FilterList(self)
        self.launcher = LauncherPanel(self)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.launcher,        0, wx.ALL|wx.EXPAND, 0)
        #box.Add(self.grid,           1, wx.ALL|wx.EXPAND, 0)
        #box.Add(self.filterList,     0, wx.ALL|wx.EXPAND, 0)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
        self.statusbar = self.CreateStatusBar()

    def __init__(self, parent):
        self.config = load_config()
        self.__init_gui(parent)

    def OnClose(self, evt):
        self.Close()

    def OnWinClose(self, evt):
        log.info("Saving config and exiting")
        save_config(self.config)
        self.Destroy()

    #def OnRefreshData(self, evt):
    #    self.grid.OnRefreshData(evt)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)19.19s %(levelname)4.4s %(message)s")
    module_log = logging.getLogger("eve_mlp")
    module_log.setLevel(logging.DEBUG)

    app = InspectableApp(False)
    frame = MainFrame(None)
    frame.Show(True)
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
