import wx
import os
import logging
import socket
from ConfigParser import SafeConfigParser
from StringIO import StringIO

from eve_mlp.common import LaunchConfig
from eve_mlp.protocol import get_packet


log = logging.getLogger(__name__)

_servers = [
    ("Tranquility", "87.237.38.200", 26000),
    ("Singularity", "87.237.38.50", 26000),
]

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

        # fetch data
        path2ver = {}
        for account in main.config.launches:
            ci = CommonIni(account.gamepath)
            path2ver[account.gamepath] = "%s.%s" % (ci.version, ci.build)

        serv2ver = {}
        for name, ip, port in _servers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, port))
                data = s.recv(4096)
                s.close()

                pkt = get_packet(StringIO(data))
                serv2ver[name] = "%.2f.%d (%d online)" % (pkt["version"], pkt["build"], pkt["online"])
            except Exception as e:
                serv2ver[name] = "Error (%s)" % e

        # client group
        client_grid = wx.FlexGridSizer(0, 2, 2, 2)
        client_grid.AddGrowableCol(0)
        client_grid.AddGrowableCol(1)

        for k, v in path2ver.items():
            client_grid.Add(wx.StaticText(self, label=k+":"), 0, wx.EXPAND)
            client_grid.Add(wx.StaticText(self, label=v), 1, wx.EXPAND)
            #client_grid.Add(wx.Button(self, label="Update"), 0, wx.EXPAND)

        # server group
        server_grid = wx.FlexGridSizer(0, 2, 2, 2)
        server_grid.AddGrowableCol(1)

        for k, v in serv2ver.items():
            server_grid.Add(wx.StaticText(self, label=k+":"), 0, wx.EXPAND)
            server_grid.Add(wx.StaticText(self, label=v), 1, wx.EXPAND)

        # put client and server groups onto the panel
        box = wx.BoxSizer(wx.VERTICAL)

        client_box = wx.StaticBoxSizer(wx.StaticBox(self, label="Client Status"), wx.VERTICAL)
        client_box.Add(client_grid, 1, wx.EXPAND)
        box.Add(client_box, 0, wx.EXPAND)

        server_box = wx.StaticBoxSizer(wx.StaticBox(self, label="Server Status"), wx.VERTICAL)
        server_box.Add(server_grid, 1, wx.EXPAND)
        box.Add(server_box, 0, wx.EXPAND)

        self.SetSizer(box)

        # go
        self.Layout()
