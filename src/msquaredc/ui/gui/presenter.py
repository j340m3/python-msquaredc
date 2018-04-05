# -*- coding: utf-8 -*-
import os
import traceback
from sys import version_info

from msquaredc.ui.interfaces import AbstractPresenter

if version_info[0] == 2:
    # We are using Python 2.x
    import Tkinter as tk
    import ttk
    import tkFileDialog as filedialog

elif version_info[0] == 3:
    # We are using Python 3.x
    import tkinter as tk
    from tkinter import ttk
    import tkinter.filedialog as filedialog


def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


class GUIPresenter(AbstractPresenter):
    def __init__(self, *args, **kwargs):
        self.tk = tk.Tk()
        self.parent = None
        super(GUIPresenter, self).__init__(name=__name__, *args, **kwargs)
        self.logger.info("Building the GUI presenter.")
        self.init_tk()
        self.args = args
        self.kwargs = kwargs
        self.logger.info("The GUI presenter has been build.")

    def __setitem__(self, key, value):
        self.widgets.__setitem__(key, value)

    def __getitem__(self, item):
        return self.widgets.__getitem__(item)

    def __iter__(self):
        return self.widgets.__iter__()

    def __len__(self):
        return self.widgets.__len__()

    def init_tk(self):
        self.logger.info("Initializing Tk")
        self.widgets = dict()
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
        top = self.tk.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.frame = tk.Frame(self.tk)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

    @property
    def wraplength(self):
        return self.tk.winfo_width()



    def build_project(self):
        self["title"] = tk.Label(self.frame, text="Please verify project details:", wraplength=self.wraplength)
        self["title"].grid(row=0)

        # All Concerning the coder
        self["lcoder"] = tk.Label(self.frame, text="Coder:")
        self["lcoder"].grid(row=1)
        self["ecoder"] = tk.Entry(self.frame)
        self["ecoder"].grid(row=2)
        if self.pb.coder is not None:
            self["ecoder"].insert(0, str(self.pb.coder))

        # All Concerning the config file
        self["lconfig"] = tk.Label(self.frame, text="Config File:")
        self["lconfig"].grid(row=3)
        self["econfig"] = tk.Entry(self.frame)
        self["econfig"].grid(row=4)

        if self.pb.config is not None:
            self["econfig"].insert(0, str(self.pb.config))

        # All Concernign data_file
        self["ldata"] = tk.Label(self.frame, text="Data File:")
        self["ldata"].grid(row=5)
        self["edata"] = tk.Entry(self.frame)
        self["edata"].grid(row=6)
        if self.pb.data is not None:
            self["edata"].insert(0, str(self.pb.data))

        self["button"] = tk.Button(self.frame, text="Submit", command=self.__cleanup_build_project)
        self["button"].grid(row=7)

    def __cleanup_build_project(self):
        config_file = self["econfig"].get()
        data_file = self["edata"].get()
        done = True
        if os.path.isfile(config_file):
            self["econfig"].config(highlightbackground="GREEN")
        else:
            done = False
            self["econfig"].config(highlightbackground="RED")
        if os.path.isfile(data_file):
            self["edata"].config(highlightbackground="GREEN")
        else:
            done = False
            self["edata"].config(highlightbackground="RED")

        if done:
            for i in self:
                self[i].destroy()

    def __cleanup_coder(self):
        for child in self.frame.winfo_children():
            child.destroy()

    """
    def get_coder(self):
        self.logger.debug("Asking coder")
        label = tk.Label(self.frame, text="Please insert coder:")
        label.grid(row=0)
        e1 = tk.Entry(self.frame)
        e1.bind("<Tab>", self.focus_next_window)
        e1.grid(row=1, column=0)
        b1 = tk.Button(self.frame, text="Save", command=self.__cleanup_get_coder)
        b1.bind("<Tab>", self.focus_next_window)
        b1.grid(row=1, column=1)
    """

    def __cleanup_get_coder(self):
        for child in self.frame.winfo_children():
            if type(child) is tk.Entry:
                self.pb["coder"] = child.get()
            child.destroy()

    def get_config_file(self):
        self.pb["config_file"] = filedialog.askopenfilename()

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

    def load_mainframe(self, project, *args, **kwargs):
        self.logger.info("Loading Mainframe.")
        self.project = project
        self.current_question = project.__next__()
        self.show_question()

    def show_question(self):
        self.logger.debug("Showing question")
        
        self["question"] = tk.Label(self.frame, text=self.current_question.question, wraplength=self.wraplength)
        self["question"].grid(row=0)
        self["answer"] = tk.Label(self.frame, text=self.current_question.answer, wraplength=self.wraplength)
        self["answer"].grid(row=1)

        for i, j in enumerate(self.current_question.coding_questions):
            self["l" + str(i)] = tk.Label(self.frame, text=j)
            self["l" + str(i)].grid(row=2 * (i + 1))
            self["e" + str(i)] = tk.Entry(self.frame)
            self["e" + str(i)].grid(row=2 * (i + 1) + 1)

        self["button"] = tk.Button(self.frame, text="Submit", command=self.__cleanup_answer_question)
        self["button"].grid(row=2 * (i + 2))

        self.logger.debug("Question shown")

    def __cleanup_answer_question(self):
        done = True

        # Some not None Checks

        if done:
            for i in self:
                self[i].destroy()
            self.show_question()

    def run(self):
        self.logger.debug("Starting GUI")
        try:
            super(GUIPresenter, self).run()
            self.tk.mainloop()
        except:
            self.logger.critical("Unhandled Error:\n{}".format(traceback.format_exc()).rstrip())
        else:
            self.logger.debug("Leaving GUI normally.")

    @staticmethod
    def focus_next_window(event):
        event.widget.tk_focusNext().focus()
        return ("break")
