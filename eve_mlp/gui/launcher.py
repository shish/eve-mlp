import wx
import wx.grid


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

        char_list = wx.grid.Grid(self, -1)
        self.char_table = CharTable(char_list, parent.config)
        char_list.SetTable(self.char_table)
        launch_all = wx.Button(self, -1, "Launch All")

        box.Add(char_list, 1)
        box.Add(launch_all, 0, wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnLaunchAll, launch_all)

        self.SetSizer(box)
        self.Layout()

    def OnLaunchAll(self, evt):
        for username in self.config["usernames"]:
            self.parent.launch(username)
