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


class GUIPresenter(AbstractPresenter):
    def __init__(self, *args, **kwargs):
        self.tk = tk.Tk()
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

    def load_mainframe(self, *args, **kwargs):
        self.logger.info("Loading Mainframe.")

    def run(self):
        self.tk.mainloop()
