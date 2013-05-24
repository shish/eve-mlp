import sys
import logging

from wx.lib.mixins.inspection import InspectableApp

from eve_mlp.gui.mainframe import MainFrame

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
