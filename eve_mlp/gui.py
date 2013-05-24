import os
import sys
import logging
from Tkinter import *
from eve_mlp.common import load_config, save_config, launch, __version__

have_ttk = False


log = logging.getLogger(__name__)


def set_icon(root, basename):
    if os.name == "nt":
        root.wm_iconbitmap(default=resource("%s.ico" % basename))


def win_center(root):
    root.update()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))


def resource(path):
    ideas = [
        os.path.join(os.path.dirname(sys.argv[0]), path),
        os.path.join(os.environ.get("_MEIPASS2", "/"), path),
        path,
    ]
    for n in range(0, 5):
        parts = ([".."] * n + [path])
        ideas.append(os.path.join(*parts))
    for p in ideas:
        if os.path.exists(p):
            return p
    return None


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


#
# main screen:
#    User  Pass
#    Abc   ***   [Launch]
#    Def   ***   [Launch]
#    [    Launch All    ]
#

class _App(object):
    def __menu(self, master):
        menubar = Menu(master)

        def server_menu():
            servermenu = Menu(menubar, tearoff=0)
            servermenu.add_radiobutton(label="Tranquility (Main)", variable=self.server, value="tranquility")
            servermenu.add_radiobutton(label="Singularity (Beta)", variable=self.server, value="singularity")
            return servermenu
        menubar.add_cascade(label="Server", menu=server_menu())

        def options_menu():
            optionsmenu = Menu(menubar, tearoff=0)
            optionsmenu.add_checkbutton(label="Remember Passwords", variable=self.remember_passwords)
            optionsmenu.add_command(label="Locate Eve Install", command=None)
            optionsmenu.add_command(label="Locate Singularity Install", command=None)
            return optionsmenu
        menubar.add_cascade(label="Options", menu=options_menu())

        def tools_menu():
            toolsmenu = Menu(menubar, tearoff=0)
            toolsmenu.add_command(label="Launch Patcher", command=None)
            return toolsmenu
        # menubar.add_cascade(label="Tools", menu=tools_menu())

        def help_menu():
            def show_about():
                t = Toplevel(master)
                t.title("About")
                t.transient(master)
                t.resizable(False, False)
                #Label(t, image=self.img_logo).grid(column=0, row=0, sticky=(E, W))
                Label(t, text="Mobile Launch Platform %s" % __version__, anchor=CENTER).grid(column=0, row=1, sticky=(E, W))
                Label(t, text="(c) 2013 Shish", anchor=CENTER).grid(column=0, row=2, sticky=(E, W))
                Button(t, text="Close", command=t.destroy).grid(column=0, row=3, sticky=(E,))
                win_center(t)

            def show_license():
                t = Toplevel(master)
                t.title("EVE-MLP Licenses")
                t.transient(master)
                scroll = Scrollbar(t, orient=VERTICAL)
                tx = Text(
                    t,
                    wrap=WORD,
                    yscrollcommand=scroll.set,
                )
                scroll['command'] = tx.yview
                scroll.pack(side=RIGHT, fill=Y, expand=1)
                tx.pack(fill=BOTH, expand=1)
                tx.insert("0.0", file(resource("LICENSE.txt")).read().replace("\r", ""))
                tx.configure(state="disabled")
                tx.focus_set()
                win_center(t)

            helpmenu = Menu(menubar, tearoff=0)
            helpmenu.add_command(label="About", command=show_about)
            helpmenu.add_command(label="License", command=show_license)
            return helpmenu
        menubar.add_cascade(label="Help", menu=help_menu())

        master.config(menu=menubar)

    def __init__(self, master):
        self.remember_passwords = BooleanVar(master, False)
        self.server = StringVar(master, "tranquility")

        self.master = master
        self.master_pass = None
        self.config = load_config()

        if self.config["passwords"]:
            self.remember_passwords.set(True)

        master.protocol("WM_DELETE_WINDOW", self.save_settings_and_quit)

        self.menu = self.__menu(master)

        #self.controls = self.__control_box(master)
        #self.menu = self.__menu(master)
        self.launch_all = Button(master, text="Launch All")
        self.status = Label(master, text="")
        if have_ttk:
            self.grip = Sizegrip(master)

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)
#        self.controls.grid(column=0, row=0, sticky=(W, E), columnspan=2)
        self.launch_all.grid(column=0, row=3, sticky=(W, E))
        self.status.grid(column=0, row=4, sticky=(W, E))
        if have_ttk:
            self.grip.grid(column=1, row=4, sticky=(S, E))

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
