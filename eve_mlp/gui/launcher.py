import wx
import wx.grid

from eve_mlp.common import Account


class CharTable(wx.grid.PyGridTableBase):
    def __init__(self, grid, main):
        wx.grid.PyGridTableBase.__init__(self)
        self.grid = grid
        self.main = main
        self.config = main.config

    def GetAttr(self, row, col, *something):
        if col == 1:
            attr = wx.grid.GridCellAttr()
            attr.SetTextColour(wx.BLUE)
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
            return attr

    def GetNumberCols(self):
        return 2

    def GetNumberRows(self):
        return len(self.config.accounts) + 1

    def GetColLabelValue(self, col):
        return ["Setup Name", "Action"][col]

    def GetRowLabelValue(self, row):
        return row

    def GetValue(self, row, col):
        if row == len(self.config.accounts):
            return ""
        if col == 0:
            return self.config.accounts[row].confname
        if col == 1:
            return "Launch!"
        return "x"

    def SetValue(self, row, col, value):
        end = len(self.config.accounts)

        # final row
        if row == end:
            if value == "":
                # final row is empty, no change
                pass
            else:
                # final row has had something added to it
                if col == 0:
                    self.config.accounts.append(Account(self.config.defaults, {"confname": value}))
                    msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 1)
                    self.grid.ProcessTableMessage(msg)
                    self.main.OnAccountSelected(row)

        # username column
        elif col == 0:
            if value == "":
                # a username has been deleted
                del self.config.accounts[row]
                msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, row, 1)
                self.grid.ProcessTableMessage(msg)
            else:
                # a username has been modified
                self.config.accounts[row].confname = value

        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.grid.ProcessTableMessage(msg)

        self.grid.ForceRefresh()


class LauncherPanel(wx.Panel):
    """
    List all the known Account objects, so the player can pick and interact with them

    Now that settings are a separate panel, it might make sense to move away from
    a spreadsheet view?
    """

    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.config = config

        box = wx.StaticBoxSizer(wx.StaticBox(self, label="Character List"), wx.VERTICAL)

        char_list = wx.grid.Grid(self, -1)
        char_list.RegisterDataType(wx.grid.GRID_VALUE_STRING, None, None)
        char_list.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        char_list.SetTable(CharTable(char_list, parent))
        char_list.SetRowLabelSize(40)
        char_list.SetColSize(0, 150)
        launch_all = wx.Button(self, -1, "Launch All")

        box.Add(char_list, 1)
        box.Add(launch_all, 0, wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnLaunchAll, launch_all)

        self.SetSizer(box)
        self.Layout()

    def OnCellLeftClick(self, evt):
        uid = evt.GetRow()
        if uid < len(self.config.accounts):
            if evt.GetCol() == 0:
                self.parent.OnAccountSelected(uid)
                # we handled it, but we also want the default action (edit this cell)
                evt.Skip(True)
            if evt.GetCol() == 1:
                self.parent.launch(self.config.accounts[uid])
                # we handled it
                evt.Skip(False)
        else:
            # we can't handle it, skip us
            evt.Skip(True)

    def OnLaunchAll(self, evt):
        for account in self.config.accounts:
            self.parent.launch(account)
