import wx
import wx.html

import requests


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

