import wx
import os
import logging
import socket
from ConfigParser import SafeConfigParser
from StringIO import StringIO

from eve_mlp.common import LaunchConfig, servers, update, LaunchFailed
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
        self.client_grid = wx.GridSizer(0, 3, 2, 2)
        #self.client_grid.AddGrowableCol(0)
        #self.client_grid.AddGrowableCol(1)
        #self.client_grid.AddGrowableCol(2)

        # server group
        self.server_grid = wx.GridSizer(0, 3, 2, 2)
        #self.server_grid.AddGrowableCol(1)

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

    def get_server_versions(self):
        all_servers_ok = True
        server_versions = {}

        for server in servers:
            try:
                logging.info("Getting version info from %s" % server.name)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((server.addr, server.port))
                data = s.recv(4096)
                s.close()

                pkt = get_packet(StringIO(data))
                version = "%.2f.%d" % (pkt["version"], pkt["build"])
                status = "%d online" % pkt["online"]
                server_versions[server.name] = (version, status)
            except Exception as e:
                server_versions[server.name] = (
                    ("?"),
                    ("Error (%s)" % e)
                )
                all_servers_ok = False

        return all_servers_ok, server_versions

    def get_client_version(self, account):
        if not account._gamepath:
            return None
        else:
            ci = CommonIni(account.gamepath)
            return "%s.%s" % (ci.version, ci.build)

    def OnRefresh(self, evt):
        all_servers_ok, server_versions = self.get_server_versions()

        self.client_grid.Clear(True)
        update_required = False
        for n, launch in enumerate([self.main.config.defaults, ] + self.main.config.launches, -1):
            version = self.get_client_version(launch)

            if version == None:
                continue

            label = "%s (%s):" % (launch.confname or "Default", launch.serverid.title())
            self.client_grid.Add(wx.StaticText(self, label=label), 0, wx.EXPAND)
            self.client_grid.Add(wx.StaticText(self, label=version), 1, wx.EXPAND)

            if version == server_versions[launch.serverid.title()]:
                self.client_grid.Add(wx.StaticText(self, label="Ok"), 1, wx.EXPAND)
            else:
                if all_servers_ok:
                    label = "Needs update"
                    update_required = True
                else:
                    label = "Needs update?"
                update = wx.Button(self, n, label=label)
                self.Bind(wx.EVT_BUTTON, self.OnUpdate, update)
                self.client_grid.Add(update, 1, wx.EXPAND)

        self.server_grid.Clear(True)
        for server, (version, status) in server_versions.items():
            self.server_grid.Add(wx.StaticText(self, label=server+":"), 2, wx.EXPAND)
            self.server_grid.Add(wx.StaticText(self, label=version), 1, wx.EXPAND)
            self.server_grid.Add(wx.StaticText(self, label=status), 1, wx.EXPAND)

        self.Layout()

        if update_required:
            self.main.tabs.SetSelection(2)

    def OnUpdate(self, evt):
        try:
            lid = evt.GetId()
            log.info("Launching launch ID %d" % lid)
            if lid == -1:
                launch = self.main.config.defaults
            else:
                launch = self.main.config.launches[lid]
            update(launch)
        except Exception as e:
            wx.MessageBox(str(e), "Update Failed", wx.OK | wx.ICON_ERROR)
