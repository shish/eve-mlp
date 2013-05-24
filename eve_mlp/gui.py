import sys
import logging

import wx
import wx.grid
import wx.html
import requests
from wx.lib.mixins.inspection import InspectableApp

from eve_mlp.common import *

#
#  20XX - menu IDs
#  30XX - launch account #XX
#

log = logging.getLogger(__name__)


def resource(path):
    ideas = [
        os.path.join(os.path.dirname(sys.argv[0]), path),
        os.path.join(os.environ.get("_MEIPASS2", "/"), path),
        path,
    ]
    for n in range(0, 5):
        parts = ([".."] * n + [path])
        ideas.append(os.path.join(*parts))
    for p in ideas:
        if os.path.exists(p):
            return p
    return None


class CharTable(wx.grid.PyGridTableBase):
    def __init__(self, grid, config):
        wx.grid.PyGridTableBase.__init__(self)
        self.grid = grid
        self.config = config

    def GetNumberCols(self):
        return 2

    def GetNumberRows(self):
        return len(self.config["usernames"]) + 1

    def GetColLabelValue(self, col):
        return ["Username", "Password", "Action"][col]

    def GetRowLabelValue(self, row):
        return row

    def GetValue(self, row, col):
        if row == len(self.config["usernames"]):
            return ""

        if col == 0:
            return self.config["usernames"][row]
        if col == 1:
            username = self.config["usernames"][row]
            if username in self.config["passwords"]:
                return "*" * 8
            else:
                return "-" * 8

        return "x"

    def SetValue(self, row, col, value):
        end = len(self.config["usernames"])

        # final row
        if row == end:
            if value == "":
                # final row is empty, no change
                pass
            else:
                # final row has had something added to it
                if col == 0:
                    self.config["usernames"].append(value)
                    msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 1)
                    self.grid.ProcessTableMessage(msg)

        # username column
        elif col == 0:
            if value == "":
                # a username has been deleted
                username = self.config["usernames"][row]
                del self.config["usernames"][row]
                if username in self.config["passwords"]:
                    del self.config["passwords"][username]
                msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, row, 1)
                self.grid.ProcessTableMessage(msg)
            else:
                # a username has been modified
                self.config["usernames"][row] = value

        # password column
        elif col == 1:
            username = self.config["usernames"][row]
            if value == "":
                # password deleted
                del self.config["passwords"][username]
            else:
                # password set
                self.config["passwords"][username] = value


        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.grid.ProcessTableMessage(msg)

        self.grid.ForceRefresh()


class LauncherPanel(wx.Panel):
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.config = config

        box = wx.StaticBoxSizer(wx.StaticBox(self, label="Character List"), wx.VERTICAL)

        char_list = wx.grid.Grid(parent, -1)
        self.char_table = CharTable(char_list, parent.config)
        char_list.SetTable(self.char_table)
        char_list.SetColLabelValue(0, "Name")
        char_list.SetColLabelValue(1, "Password")
        char_list.SetColLabelValue(2, "Action")
        launch_all = wx.Button(self, -1, "Launch All")

        box.Add(char_list, 1)
        box.Add(launch_all, 0, wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnLaunchAll, launch_all)

        self.SetSizer(box)
        self.Layout()

    def OnLaunchAll(self, evt):
        for username in self.config["usernames"]:
            self.parent.launch(username)


class NewsPanel(wx.Panel):
    def add_http_panel(self, url, name):
#        https://client.eveonline.com/launcherv3
#        DIV.overview>ARTICLE.news
        html = wx.html.HtmlWindow(self.nb)
        try:
            # TODO: async load
            data = requests.get(url).text
        except Exception as e:
            data = "Couldn't get %s:\n%s" % (url, str(e))
        html.SetPage(data)
        self.nb.AddPage(html, name)

    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent)
        self.config = config

        self.nb = wx.Notebook(self)

        self.add_http_panel("http://code.shishnet.org/eve-mlp/news.html", "MLP News")

        box = wx.StaticBoxSizer(wx.StaticBox(self, label="News"), wx.VERTICAL)
        box.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(box)
        self.Layout()


class Icon(wx.TaskBarIcon):
    def __init__(self, parent):
        wx.TaskBarIcon.__init__(self)
        self.parent = parent
        self.config = parent.config
        self.SetIcon(wx.Icon(resource("icon.ico"), wx.BITMAP_TYPE_ICO), "Mobile Launcher Platform")
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnLeftDClick)
        self.CreateMenu()

    def CreateMenu(self):
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnPopup)
        self.menu = wx.Menu()

        for n, username in enumerate(self.config["usernames"]):
            m_launch = self.menu.Append(3000 + n, 'Launch '+username)
            self.Bind(wx.EVT_MENU, self.OnLaunch, m_launch)

        self.menu.AppendSeparator()
        m_exit = self.menu.Append(wx.ID_EXIT, 'E&xit')

        self.Bind(wx.EVT_MENU, self.parent.OnClose, m_exit)

    def OnPopup(self, event):
        self.PopupMenu(self.menu)

    def OnLeftDClick(self, evt):
        if self.parent.IsShown():
            self.parent.Hide()
        else:
            self.parent.Show()

    def OnLaunch(self, evt):
        self.parent.launch(self.config["usernames"][3000 - evt.GetId()])


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
        m_loc_tranq = menu.Append(2021, "Locate Eve Install", "")
        m_loc_singu = menu.Append(2022, "Locate Singularity Install", "")
        if self.remember_passwords:
            menu.Check(2020, True)
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

        self.icon = Icon(self)

    def __init__(self, parent):
        self.config = load_config()
        self.master_password = None
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
        password = self.config["passwords"].get(username)
        if username and password:
            from mock import Mock
            #token = do_login(username, password)
            token = "TOKEN"
            launch(token, Mock(dry=True, singularity=False))

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
        self.icon.Destroy()
        self.Destroy()

    def OnToggleRememberPasswords(self, evt):
        self.remember_passwords = evt.GetEventObject().IsChecked(2020)

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
        except:
            info.SetLicense("MIT")
        wx.AboutBox(info)


def main(args=sys.argv):
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)19.19s %(levelname)4.4s %(message)s")
    module_log = logging.getLogger("eve_mlp")
    module_log.setLevel(logging.DEBUG)

    app = InspectableApp(False)
    frame = MainFrame(None)
    frame.Show(True)
    #import wx.lib.inspection
    #wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
