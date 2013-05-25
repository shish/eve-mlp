import sys
import logging

import wx
import wx.grid
import wx.html
import requests

from eve_mlp.common import *
from eve_mlp.login import do_login, LoginFailed
from eve_mlp.gui.trayicon import TrayIcon
from eve_mlp.gui.launcher import LauncherPanel
from eve_mlp.gui.news import NewsPanel
from eve_mlp.gui.common import resource


#
#  20XX - menu IDs
#  30XX - launch account #XX
#

log = logging.getLogger(__name__)


class MainFrame(wx.Frame):
    def __menu(self):
        menu_bar = wx.MenuBar()

        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menu_bar.Append(menu, "&File")

        menu = wx.Menu()
        m_tranq = menu.Append(2010, "Tranquility (Main)", "", kind=wx.ITEM_RADIO)
        m_singu = menu.Append(2011, "Singularity (Beta)", "", kind=wx.ITEM_RADIO)
        def setServer(s):
            log.info("Setting server to: %s", s)
            self.server = s
        self.Bind(wx.EVT_MENU, lambda e: setServer("tranquility"), m_tranq)
        self.Bind(wx.EVT_MENU, lambda e: setServer("singularity"), m_singu)
        menu_bar.Append(menu, "&Server")

        menu = wx.Menu()
        m_rempasswd = menu.Append(2020, "Remember Passwords", "", kind=wx.ITEM_CHECK)
        self.m_rempasswd = m_rempasswd  # event handler needs this object, not just ID?
        m_loc_tranq = menu.Append(2021, "Locate Eve Install", "")
        m_loc_singu = menu.Append(2022, "Locate Singularity Install", "")
        if self.remember_passwords:
            m_rempasswd.Check(True)
        def setDir(name):
            dd = wx.DirDialog(self, "Pick a game folder", self.config.get(name+"-dir", ""))
            if dd.ShowModal() == wx.ID_OK:
                log.info("Setting %s dir to %s", name, dd.GetPath())
                self.config[name+"-dir"] = dd.GetPath()
            dd.Destroy()
        self.Bind(wx.EVT_MENU, lambda e: setDir("eve"), m_loc_tranq)
        self.Bind(wx.EVT_MENU, lambda e: setDir("singularity"), m_loc_singu)
        self.Bind(wx.EVT_MENU, self.OnToggleRememberPasswords, m_rempasswd)
        menu_bar.Append(menu, "&Options")

        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "Launch Patcher", "")
        m_exit = menu.Append(wx.ID_EXIT, "Launch Repair", "")
        #self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        #menu_bar.Append(menu, "&Tools")

        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menu_bar.Append(menu, "&Help")

        return menu_bar

    def __init_gui(self, parent):
        wx.Frame.__init__(self, parent, -1, "Mobile Launch Platform", size=(640, 480))
        self.Bind(wx.EVT_CLOSE, self.OnWinClose)

        self.SetMenuBar(self.__menu())

        self.launcher = LauncherPanel(self, self.config)
        self.news = NewsPanel(self, self.config)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.launcher,        0, wx.ALL|wx.EXPAND, 0)
        box.Add(self.news,            1, wx.ALL|wx.EXPAND, 0)

        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
        self.statusbar = self.CreateStatusBar()

        try:
            self.icon = TrayIcon(self)
        except:
            self.icon = None

    def __init__(self, parent):
        self.config = load_config()
        self.master_pass = None
        self.server = "tranquility"

        if self.config["passwords"]:
            self.remember_passwords = True
            ped = wx.PasswordEntryDialog(parent, "Enter Master Password")
            ped.ShowModal()
            self.master_pass = ped.GetValue()
            ped.Destroy()
            for key in self.config["passwords"]:
                self.config["passwords"][key] = decrypt(self.config["passwords"][key], self.master_pass)
        else:
            self.remember_passwords = False

        self.__init_gui(parent)

    def launch(self, username):
        if username in self.config["passwords"]:
            password = self.config["passwords"][username]
        else:
            ped = wx.PasswordEntryDialog(self, "Enter %s's Password" % username)
            ped.ShowModal()
            password = ped.GetValue()
            ped.Destroy()

        if username and password:
            from mock import Mock
            if self.server == "tranquility":
                di = self.config.get("eve-dir")
                singularity = False
            else:
                di = self.config.get("singularity-dir")
                singularity = True

            if di and os.path.exists(di):
                os.chdir(di)

            if os.path.exists(os.path.join("bin", "ExeFile.exe")):
                try:
                    token = do_login(username, password)
                    #token = "TOKEN"
                    launch(token, Mock(dry=False, singularity=singularity))
                except LoginFailed as e:
                    wx.MessageBox(str(e), "%s: Login Failed" % username, wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox("Can't find bin/ExeFile.exe.\nTry 'Options' -> 'Locate Eve Install'?", "Launch Failed", wx.OK | wx.ICON_ERROR)

                print "Not in the right directory"

    def OnClose(self, evt):
        self.Close()

    def OnWinClose(self, evt):
        log.info("Saving config and exiting")
        if self.remember_passwords:
            for key in self.config["passwords"]:
                self.config["passwords"][key] = encrypt(self.config["passwords"][key], self.master_pass)
        else:
            self.config["passwords"] = {}

        save_config(self.config)
        if self.icon:
            self.icon.Destroy()
        self.Destroy()

    def OnToggleRememberPasswords(self, evt):
        self.remember_passwords = self.m_rempasswd.IsChecked()
        if not self.master_pass:
            ped = wx.PasswordEntryDialog(self, "Set Master Password")
            ped.ShowModal()
            self.master_pass = ped.GetValue()
            ped.Destroy()

    def OnAbout(self, evt):
        import eve_mlp.common as common
        info = wx.AboutDialogInfo()
        info.SetName("Mobile Launch Platform")
        info.SetDescription("A cross-platform EVE Online launcher")
        info.SetVersion(common.__version__)
        info.SetCopyright("(c) Shish 2013 ('Shish Tukay' in game)")
        info.SetWebSite("https://github.com/shish/eve-mlp")
        info.AddDeveloper("Shish <webmaster@shishnet.org>")
        # info.SetIcon()
        try:
            info.SetLicense(file(resource("LICENSE.txt")).read())
        except Exception as e:
            log.exception("Error getting license:")
            info.SetLicense("MIT")
        wx.AboutBox(info)
