# -*- coding: utf-8 -*-
from sys import version_info
from msquaredc.ui.interfaces import AbstractPresenter

if version_info[0] == 2:
    # We are using Python 2.x
    import Tkinter as tk
    import ttk

elif version_info[0] == 3:
    # We are using Python 3.x
    import tkinter as tk
    from tkinter import ttk

def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

class GUIPresenter(AbstractPresenter):
    def __init__(self, *args, **kwargs):
        self.tk = tk.Tk()
        self.parent = None
        super(GUIPresenter, self).__init__(name=__name__, *args, **kwargs)
        self.logger.info("Building the GUI presenter.")
        self.init_tk()
        self.logger.info("The GUI presenter has been build.")

    def init_tk(self):
        self.logger.info("Initializing Tk")
        self.tk.title("M²C")
        self.tk.geometry("640x480")
        self.tk.style = ttk.Style()
        self.tk.style.theme_use("clam")
        self.logger.debug("Loading Keybindings")
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.logger.debug("Keybindings loaded")
        self.__is_fullscreen = False
        self.logger.info("Tk initialized")
        center(self.tk)
        self.frame = tk.Frame(self.tk)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.ask_coder()

    def show_question(self, question):
        pass

    def ask_coder(self):
        label = tk.Label(self.frame, text="Please insert coder:")
        label.grid(row=0)
        e1 = tk.Entry(self.frame)
        e1.grid(row=1, column=0)
        b1 = tk.Button(self.frame, text="Save", command=self.cleanup_ask_coder)
        b1.grid(row=1, column=1)

    def cleanup_ask_coder(self):
        for child in self.frame.winfo_children():
            if type(child) is tk.Entry:
                self.coder = child.get()
            child.destroy()

    def toggle_fullscreen(self, event=None):
        self.logger.debug("Toggling Fullscreen to {}.".format(not self.__is_fullscreen))
        self.__is_fullscreen = not self.__is_fullscreen  # Just toggling the boolean
        self.tk.attributes('-fullscreen', self.__is_fullscreen)
        self.tk.overrideredirect(self.__is_fullscreen)
        return "break"

    def end_fullscreen(self, event=None):
        if self.__is_fullscreen:
            self.logger.debug("Leaving fullscreen mode.")
            self.__is_fullscreen = False
            self.tk.attributes("-fullscreen", False)
            self.tk.overrideredirect(False)
        return "break"

    def new_project_wizard(self, path=None):
        self.logger.info("Creating a new Project.")

    def load_mainframe(self,project, *args, **kwargs):
        self.logger.info("Loading Mainframe.")
        self.project = project

    def run(self):
        self.logger.debug("Starting GUI")
        try:
            self.tk.mainloop()
        except Exception as e:
            self.logger.critical("Unhandled Error:{}".format(str(e)))
        else:
            self.logger.debug("Leaving GUI normally.")

    def getCoder(self):
        master = tk.Tk("Coder")
        tk.Label(master, text="Please insert coder name:").grid(row=0)
        e1 = tk.Entry(master)
        e1.grid(row=0,column=1)
        b1 = tk.Button(master,text="Save",command=master.destroy)
        b1.grid(row=0,column=2)
        master.call('wm', 'attributes', '.', '-topmost', '1')
        center(master)
        master.mainloop()
        return e1.get(),False
