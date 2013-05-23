import sys
import logging
from Tkinter import *


log = logging.getLogger(__name__)


#
# if passwords saved:
#    Enter master password
#    [                   ]
#                   Unlock
#
# main screen:
#    User  Pass          
#    Abc   ***   [Launch]
#    Def   ***   [Launch]
#    [    Launch All    ]
#
#    menu:
#       server
#          tranquility (live)
#          singularity (beta)
#       options
#          locate eve install
#          locate singularity install
#          (x) remember passwords
#       tools
#          launch official patcher
#

def main(args=sys.argv):
    root = Tk()

    w = Label(root, text="Hello, world!")
    w.pack()

    root.mainloop()
