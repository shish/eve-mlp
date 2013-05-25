import sys
import logging

import wx
import wx.grid
import wx.html
import requests

from eve_mlp.common import *
from eve_mlp.common import __version__
from eve_mlp.gui.common import *

from eve_mlp.login import do_login, LoginFailed
from eve_mlp.gui.trayicon import TrayIcon
from eve_mlp.gui.launcher import LauncherPanel
from eve_mlp.gui.news import NewsPanel
from eve_mlp.gui.account import AccountPanel


#
#  20XX - menu IDs
#  30XX - launch account #XX
#

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
        try:
            # give this process an ID other than "python", else
            # windows 7 will give it the python icon and group it
            # with other python windows in the task bar
            import ctypes
            myappid = 'code.shishnet.org/eve-mlp'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            pass
        
        wx.Frame.__init__(self, parent, -1, "Mobile Launch Platform [%s]" % __version__, size=(640, 480))
        self.Bind(wx.EVT_CLOSE, self.OnWinClose)
        try:
            self.SetIcons(icon_bundle(resource("icon.ico")))
        except Exception as e:
            pass

        self.SetMenuBar(self.__menu())

        self.launcher = LauncherPanel(self, self.config)
        self.news = NewsPanel(self, self.config)
        self.acctedit = AccountPanel(self, False)
        if not self.config.accounts:
            self.config.accounts.append(Account(self.config.defaults, {"confname": "Main Setup"}))
        self.acctedit.set_account(self.config.accounts[0])
        self.defaults = AccountPanel(self, True)
        self.defaults.set_account(self.config.defaults)

        left_box = wx.BoxSizer(wx.VERTICAL)
        left_box.Add(self.launcher, 1, wx.ALL|wx.EXPAND, 0)
        left_box.Add(self.acctedit, 0, wx.ALL|wx.EXPAND, 0)
        left_box.Add(self.defaults, 0, wx.ALL|wx.EXPAND, 0)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(left_box,             0, wx.ALL|wx.EXPAND, 0)
        box.Add(self.news,            1, wx.ALL|wx.EXPAND, 0)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
        self.statusbar = self.CreateStatusBar()

        show = True
        try:
            self.icon = TrayIcon(self)
            if self.config.settings["start-tray"]:
                log.info("Start-in-tray enabled, hiding main window")
                show = False
        except Exception as e:
            log.exception("Failed to create tray icon:")
            self.icon = None

        if show:
            self.Show(True)

    def __init__(self, parent):
        self.config = Config()
        self.config.load()
        if self.config.settings["remember-passwords"]:
            self.config.master_password = get_password(parent, "Enter Master Password")
            self.config.decrypt_passwords()
        self.__init_gui(parent)

    def launch(self, account):
        try:
            token = None
            if account.username and account.password:
                token = do_login(account.username, account.password)
            launch(self.config, account, token)
        except LoginFailed as e:
            wx.MessageBox(str(e), "%s: Login Failed" % account.confname, wx.OK | wx.ICON_ERROR)
        except LaunchFailed as e:
            wx.MessageBox(str(e), "%s: Launch Failed" % account.confname, wx.OK | wx.ICON_ERROR)

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

    def OnAccountSelected(self, idx):
        self.acctedit.set_account(self.config.accounts[idx])

    def OnAbout(self, evt):
        import eve_mlp.common as common
        info = wx.AboutDialogInfo()
        info.SetName("Mobile Launch Platform")
        info.SetDescription("A cross-platform EVE Online launcher")
        info.SetVersion(common.__version__)
        info.SetCopyright("(c) Shish 2013 ('Shish Tukay' in game)")
        info.SetWebSite("https://github.com/shish/eve-mlp")
        info.AddDeveloper("Shish <webmaster@shishnet.org>")
        
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
