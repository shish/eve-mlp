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
            self.build = cr.get("main", "version")
            self.build = cr.get("main", "build")
        except:
            self.version = None
            self.build = None


class StatusPanel(wx.Panel):
    def __init__(self, parent, main):
        wx.Panel.__init__(self, parent)

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

        box = wx.FlexGridSizer(0, 2, 2, 2)
        box.AddGrowableCol(0)
        box.AddGrowableCol(1)

        self.client_ver_lbl = wx.StaticText(self, label="Client Versions")
        self.client_ver_box = wx.StaticText(self, label="\n".join([k + ": " + str(v) for k, v in path2ver.items()]))
        self.server_ver_lbl = wx.StaticText(self, label="Server Versions")
        self.server_ver_box = wx.StaticText(self, label="\n".join([k + ": " + str(v) for k, v in serv2ver.items()]))

        box.Add(self.client_ver_lbl, 0, wx.EXPAND)
        box.Add(self.client_ver_box, 1, wx.EXPAND)
        box.Add(self.server_ver_lbl, 0, wx.EXPAND)
        box.Add(self.server_ver_box, 1, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()
