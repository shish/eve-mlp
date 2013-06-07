import wx
import os
import logging
import socket
from ConfigParser import SafeConfigParser
from StringIO import StringIO

from eve_mlp.common import LaunchConfig, servers
from eve_mlp.protocol import get_packet


log = logging.getLogger(__name__)


class CommonIni(object):
    def __init__(self, path):
        cr = SafeConfigParser()
        try:
            cr.read(path + "/common.ini")
            self.version = cr.get("main", "version")
            self.build = cr.get("main", "build")
        except:
            self.version = None
            self.build = None


class StatusPanel(wx.Panel):
    def __init__(self, parent, main):
        wx.Panel.__init__(self, parent)
        self.main = main

        # client group
        self.client_grid = wx.FlexGridSizer(0, 2, 2, 2)
        self.client_grid.AddGrowableCol(0)
        self.client_grid.AddGrowableCol(1)

        # server group
        self.server_grid = wx.FlexGridSizer(0, 2, 2, 2)
        self.server_grid.AddGrowableCol(1)

        # refresh button
        refresh = wx.Button(self, label="Refresh")
        self.Bind(wx.EVT_BUTTON, self.OnRefresh, refresh)

        # put client and server groups onto the panel
        box = wx.BoxSizer(wx.VERTICAL)

        client_box = wx.StaticBoxSizer(wx.StaticBox(self, label="Client Status"), wx.VERTICAL)
        client_box.Add(self.client_grid, 1, wx.EXPAND)
        box.Add(client_box, 0, wx.EXPAND)

        server_box = wx.StaticBoxSizer(wx.StaticBox(self, label="Server Status"), wx.VERTICAL)
        server_box.Add(self.server_grid, 1, wx.EXPAND)
        box.Add(server_box, 0, wx.EXPAND)

        box.AddStretchSpacer()

        box.Add(refresh, 0, wx.EXPAND)
        self.SetSizer(box)

        # go
        self.Layout()

        self.OnRefresh(None)

    def OnRefresh(self, evt):
        # fetch data
        path2ver = {}
        for account in self.main.config.launches:
            ci = CommonIni(account.gamepath)
            path2ver[account.gamepath] = "%s.%s" % (ci.version, ci.build)

        serv2ver = {}
        for server in servers:
            try:
                logging.info("Getting version info from %s" % server.name)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((server.addr, server.port))
                data = s.recv(4096)
                s.close()

                pkt = get_packet(StringIO(data))
                serv2ver[server.name] = "%.2f.%d (%d online)" % (pkt["version"], pkt["build"], pkt["online"])
            except Exception as e:
                serv2ver[server.name] = "Error (%s)" % e

        self.client_grid.Clear(True)
        for k, v in path2ver.items():
            self.client_grid.Add(wx.StaticText(self, label=k+":"), 0, wx.EXPAND)
            self.client_grid.Add(wx.StaticText(self, label=v), 1, wx.EXPAND)
            #client_grid.Add(wx.Button(self, label="Update"), 0, wx.EXPAND)

        self.server_grid.Clear(True)
        for k, v in serv2ver.items():
            self.server_grid.Add(wx.StaticText(self, label=k+":"), 0, wx.EXPAND)
            self.server_grid.Add(wx.StaticText(self, label=v), 1, wx.EXPAND)

        self.Layout()
