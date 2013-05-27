import wx
import wx.html

import requests


# https://client.eveonline.com/launcherv3
# DIV.overview>ARTICLE.news

class NewsPanel(wx.html.HtmlWindow):
    def __init__(self, parent, url):
        html = wx.html.HtmlWindow.__init__(self, parent)
        try:
            # TODO: async load
            data = requests.get(url).text
        except Exception as e:
            data = "Couldn't get %s:\n%s" % (url, str(e))
        self.SetPage(data)
