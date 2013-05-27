import wx
import wx.grid

from eve_mlp.common import LaunchConfig


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
        return len(self.config.launches) + 1

    def GetColLabelValue(self, col):
        return ["Setup Name", "Action"][col]

    def GetRowLabelValue(self, row):
        return row

    def GetValue(self, row, col):
        if row == len(self.config.launches):
            return ""
        if col == 0:
            return self.config.launches[row].confname
        if col == 1:
            return "Launch!"
        return "x"

    def SetValue(self, row, col, value):
        end = len(self.config.launches)

        # final row
        if row == end:
            if value == "":
                # final row is empty, no change
                pass
            else:
                # final row has had something added to it
                if col == 0:
                    self.config.launches.append(LaunchConfig(self.config.defaults, {"confname": value}))
                    msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, 1)
                    self.grid.ProcessTableMessage(msg)
                    self.main.OnLaunchConfigSelected(row)

        # username column
        elif col == 0:
            if value == "":
                # a username has been deleted
                del self.config.launches[row]
                msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, row, 1)
                self.grid.ProcessTableMessage(msg)
            else:
                # a username has been modified
                self.config.launches[row].confname = value

        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.grid.ProcessTableMessage(msg)

        self.grid.ForceRefresh()


class CharGrid(wx.grid.Grid):
    def __init__(self, parent, main):
        wx.grid.Grid.__init__(self, parent, -1)

        self.parent = parent
        self.main = main
        self.config = main.config

        self.RegisterDataType(wx.grid.GRID_VALUE_STRING, None, None)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.SetTable(CharTable(self, main))
        self.SetRowLabelSize(40)
        self.SetColSize(0, 150)

    def OnCellLeftClick(self, evt):
        uid = evt.GetRow()
        if uid < len(self.config.launches):
            if evt.GetCol() == 0:
                # click a launchconfig name
                self.main.OnLaunchConfigSelected(uid)
                # we handled it, but we also want the default action (edit this cell)
                evt.Skip(True)
            if evt.GetCol() == 1:
                # click a launch button
                self.main.launch(self.config.launches[uid])
                # we handled it
                evt.Skip(False)
        else:
            # we can't handle it, skip us
            evt.Skip(True)
