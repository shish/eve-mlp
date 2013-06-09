import sys
import logging

import wx
import wx.grid
import wx.html
import requests

from eve_mlp import __version__
from eve_mlp.common import *
from eve_mlp.gui.common import *

from eve_mlp.login import do_login, LoginFailed
from eve_mlp.gui.trayicon import TrayIcon
from eve_mlp.gui.launcher import LauncherPanel
from eve_mlp.gui.news import NewsPanel
from eve_mlp.gui.config import ConfigPanel
from eve_mlp.gui.status import StatusPanel


log = logging.getLogger(__name__)


class MainFrame(wx.Frame):
    def __menu(self):
        menu_bar = wx.MenuBar()

        ################################################################
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menu_bar.Append(menu, "&File")

        ################################################################
        menu = wx.Menu()

        m_rempasswd = menu.Append(2020, "Remember Passwords", "", kind=wx.ITEM_CHECK)
        self.m_rempasswd = m_rempasswd  # event handler needs this object, not just ID?
        if self.config.settings["remember-passwords"]:
            m_rempasswd.Check(True)
        self.Bind(wx.EVT_MENU, self.OnToggleRememberPasswords, m_rempasswd)

        m_start_tray = menu.Append(2021, "Start in Systray", "", kind=wx.ITEM_CHECK)
        self.m_start_tray = m_start_tray  # event handler needs this object, not just ID?
        if self.config.settings["start-tray"]:
            m_start_tray.Check(True)
        self.Bind(wx.EVT_MENU, self.OnToggleStartTray, m_start_tray)

        menu_bar.Append(menu, "&Options")

        ################################################################
        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "Launch Patcher", "")
        m_exit = menu.Append(wx.ID_EXIT, "Launch Repair", "")
        #self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        #menu_bar.Append(menu, "&Tools")

        ################################################################
        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menu_bar.Append(menu, "&Help")

        return menu_bar

    def __init_gui(self, parent):
        # init window
        try:
            # give this process an ID other than "python", else
            # windows 7 will give it the python icon and group it
            # with other python windows in the task bar
            import ctypes
            myappid = 'code.shishnet.org/eve-mlp'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            pass

        wx.Frame.__init__(self, parent, -1, "Mobile Launch Platform [%s]" % __version__, size=(800, 600))
        self.Bind(wx.EVT_CLOSE, self.OnWinClose)
        try:
            self.SetIcons(icon_bundle(resource("icon.ico")))
        except Exception as e:
            pass

        # bars
        self.SetMenuBar(self.__menu())
        self.statusbar = self.CreateStatusBar()

        # body of the window
        self.launcher = LauncherPanel(self, self.config)
        self.tabs = wx.Notebook(self)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.launcher, 0, wx.EXPAND)
        box.Add(self.tabs, 1, wx.EXPAND)
        #self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        # add content to tabs
        self.news_panel = NewsPanel(self.tabs, "http://code.shishnet.org/eve-mlp/news.html")
        self.config_panel = ConfigPanel(self.tabs, self)
        self.status_panel = StatusPanel(self.tabs, self)
        self.help_panel = NewsPanel(self.tabs, resource("help.html"))

        self.tabs.AddPage(self.news_panel, "MLP News")
        self.tabs.AddPage(self.config_panel, "Settings")
        self.tabs.AddPage(self.status_panel, "Status")
        self.tabs.AddPage(self.help_panel, "Help")

        # show the window and tray icon (if desired)
        show = True
        try:
            self.icon = TrayIcon(self)
            if self.config.settings["start-tray"]:
                log.info("Start-in-tray enabled, hiding main window")
                show = False
        except Exception as e:
            log.exception("Failed to create tray icon:")
            self.icon = None

        self.status_panel.OnRefresh(None)

        if show:
            self.Show(True)

    def __init__(self, parent):
        self.config = Config()
        self.config.load()
        if self.config.settings["remember-passwords"]:
            self.config.master_password = get_password(parent, "Enter Master Password")
            self.config.decrypt_passwords()
        self.__init_gui(parent)

    def launch(self, launch_config):
        try:
            token = None
            if launch_config.username and launch_config.password:
                token = do_login(launch_config.username, launch_config.password)
            launch(self.config, launch_config, token)
        except LoginFailed as e:
            wx.MessageBox(str(e), "%s: Login Failed" % launch_config.confname, wx.OK | wx.ICON_ERROR)
        except LaunchFailed as e:
            wx.MessageBox(str(e), "%s: Launch Failed" % launch_config.confname, wx.OK | wx.ICON_ERROR)

    def OnClose(self, evt):
        self.Close()

    def OnWinClose(self, evt):
        log.info("Saving config and exiting")

        self.config.encrypt_passwords()
        self.config.save()

        if self.icon:
            self.icon.Destroy()
        self.Destroy()

    def OnToggleRememberPasswords(self, evt):
        self.config.settings["remember-passwords"] = self.m_rempasswd.IsChecked()
        if self.config.settings["remember-passwords"]:
            self.config.master_password = get_password(self, "Set Master Password")

    def OnToggleStartTray(self, evt):
        self.config.settings["start-tray"] = self.m_start_tray.IsChecked()

    def OnLaunchConfigSelected(self, idx):
        self.config_panel.launch_config_edit.set_launch_config(self.config.launches[idx])
        self.tabs.SetSelection(1)

    def OnAbout(self, evt):
        import eve_mlp.common as common
        info = wx.AboutDialogInfo()
        info.SetName("Mobile Launch Platform")
        info.SetDescription("A cross-platform EVE Online launcher")
        info.SetVersion(__version__)
        info.SetCopyright("(c) Shish 2013 ('Shish Tukay' in game)")
        info.SetWebSite("https://github.com/shish/eve-mlp")
        info.AddDeveloper("Shish <webmaster@shishnet.org>")

        # Had some trouble with pyinstaller not putting these resources
        # in the places they should be, so make sure we can live without
        # them until the pyinstaller config gets fixed
        try:
            info.SetIcon(wx.Icon(resource("icon.ico"), wx.BITMAP_TYPE_ICO))
        except Exception as e:
            log.exception("Error getting icon:")

        try:
            info.SetLicense(file(resource("LICENSE.txt")).read())
        except Exception as e:
            log.exception("Error getting license:")
            info.SetLicense("MIT")

        wx.AboutBox(info)
