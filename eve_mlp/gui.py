import sys
import logging
from Tkinter import *
from eve_mlp.common import load_config, save_config, launch


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

class Unlock(Toplevel):
    def __create_widgets(self):
        self.password = StringVar()

        def unlock(*args):
            if self.callback(self.password.get()):
                self.destroy()
            else:
                self.password.set("")

        label = Label(self, text="Enter Master Password")
        label.pack(side="top", fill=BOTH)

        password_box = Entry(self, show="*", textvariable=self.password)
        password_box.bind('<Key-Return>', unlock)
        password_box.pack(side="top", fill=BOTH)
        password_box.focus_set()

        unlock = Button(self, text="Unlock", command=unlock)
        unlock.pack(side="top", fill=BOTH)

        def die(*args):
            self.destroy()
            self.master.destroy()
        self.protocol("WM_DELETE_WINDOW", die)

    def __init__(self, master, callback):
        Toplevel.__init__(self, master)
        self.title("Unlock")
        self.master = master
        self.callback = callback
        self.__create_widgets()


class _App(object):
    def __init__(self, master):
        self.master = master
        self.master_pass = None
        self.config = load_config()

        master.protocol("WM_DELETE_WINDOW", self.save_settings_and_quit)


        #self.controls = self.__control_box(master)
        #self.menu = self.__menu(master)
        #if have_ttk:
        #    self.grip = Sizegrip(master)
        #self.scrubber = self.__scrubber(master)
        self.status = Label(master, text="This is some placeholder text\nra ra ra mooo")

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)
#        self.controls.grid(column=0, row=0, sticky=(W, E), columnspan=2)
#        self.canvas.grid(column=0, row=1, sticky=(N, W, E, S))
#        self.v.grid(column=1, row=1, sticky=(N, S))
#        self.h.grid(column=0, row=2, sticky=(W, E))
#        self.scrubber.grid(column=0, row=3, sticky=(W, E), columnspan=2)
        self.status.grid(column=0, row=4, sticky=(W, E))
#        if have_ttk:
#            self.grip.grid(column=1, row=4, sticky=(S, E))

        self.master.update()

        if self.config["passwords"]:
            self.master.withdraw()
            #self.master.overrideredirect(True)

            def unlock(password):
                self.master_pass = password
                #self.master.update()
                self.master.deiconify()
                #self.master.overrideredirect(False)
                return True
            unlocker = Unlock(self.master, unlock)


    def save_settings_and_quit(self, *args):
        print "Saving settings and quitting"
        save_config(self.config)
        self.master.destroy()
        self.master.quit()

    def set_status(self, text):
        if text:
            print(text)
        self.status.config(text=text)
        self.master.update()


def main(args=sys.argv):
    root = Tk()
    #set_icon(root, "images/tools-icon")
    root.title("EVE-MLP")
    _App(root)
    root.mainloop()
