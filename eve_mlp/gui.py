import sys
import logging    
from Tkinter import *

log = logging.getLogger(__name__)

def main(args=sys.argv):
    root = Tk()

    w = Label(root, text="Hello, world!")
    w.pack()

    root.mainloop()
