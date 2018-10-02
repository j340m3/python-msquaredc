# -*- coding: utf-8 -*-
import os
import tkinter
import tkinter.filedialog
import tkinter.ttk
import traceback

from msquaredc.ui.interfaces import AbstractPresenter


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
        self.tk = tkinter.Tk()
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
        self.tk.style = tkinter.ttk.Style()
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
        self.frame = tkinter.Frame(self.tk)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

    @property
    def wraplength(self):
        return self.tk.winfo_width()

    def build_project(self):
        self["title"] = tkinter.Label(self.frame, text="Please verify project details:", wraplength=self.wraplength)
        self["title"].grid(row=0)

        # All Concerning the coder
        self["lcoder"] = tkinter.Label(self.frame, text="Coder:")
        self["lcoder"].grid(row=1)
        self["ecoder"] = tkinter.Entry(self.frame)
        self["ecoder"].grid(row=2)
        if self.pb.coder is not None:
            self["ecoder"].insert(0, str(self.pb.coder))

        # All Concerning the config file
        self["lconfig"] = tkinter.Label(self.frame, text="Config File:")
        self["lconfig"].grid(row=3)
        self["econfig"] = tkinter.Entry(self.frame)
        self["econfig"].grid(row=4)

        if self.pb.config is not None:
            self["econfig"].insert(0, str(self.pb.config))

        # All Concernign data_file
        self["ldata"] = tkinter.Label(self.frame, text="Data File:")
        self["ldata"].grid(row=5)
        self["edata"] = tkinter.Entry(self.frame)
        self["edata"].grid(row=6)
        if self.pb.data is not None:
            self["edata"].insert(0, str(self.pb.data))

        self["button"] = tkinter.Button(self.frame, text="Submit", command=self.__cleanup_build_project)
        self["button"].grid(row=7)

    def __cleanup_build_project(self):
        config_file = self["econfig"].get()
        data_file = self["edata"].get()
        done = True
        done = done and self.feedback_file_correctness("econfig", config_file)
        done = done and self.feedback_file_correctness("edata", data_file)
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
            if type(child) is tkinter.Entry:
                self.pb["coder"] = child.get()
            child.destroy()

    def get_config_file(self):
        self.pb["config_file"] = tkinter.filedialog.askopenfilename()

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
        self.show_question()

    def show_end(self):
        self["info"] = tkinter.Label(self.frame, text="Finished Coding!", wraplength=self.wraplength)
        self["info"].grid(row=0)
        self["export"] = tkinter.Button(self.frame, text="Export!", command=self.project.export)
        self["export"].grid(row=1, padx=5, pady=5, ipadx=10, ipady=10)

    def show_question(self, command="resume"):
        self.logger.debug("Showing question")
        try:
            if command == "next_new":
                self.current_question = self.project.next_new()
            elif command == "next":
                self.current_question = self.project.next()
            elif command == "previous":
                self.current_question = self.project.previous()
            elif command == "resume":
                self.current_question = self.project.resume()
        except StopIteration:
            self.logger.debug("Reached end of the Coding. Showing the end screen.")
            self.show_end()
        else:
            self["question"] = tkinter.Label(self.frame, text=self.current_question.question.text,
                                             wraplength=self.wraplength,
                                             font=("Sans", 16, "bold"))
            self["question"].grid(row=0, padx=5, pady=5)
            self["answer"] = tkinter.Label(self.frame, text=self.current_question.answer.text,
                                           wraplength=self.wraplength,
                                           font=("Sans", 16, "bold"))
            self["answer"].grid(row=1, padx=5, pady=5)
            self["helper"] = tkinter.Frame(self.frame)
            self["helper"].grid(row=2)
            for i, criteria in enumerate(self.current_question.criterias):
                self["l" + str(i)] = tkinter.Label(self["helper"], text=criteria.text, font=("Sans", 20))
                self["l" + str(i)].grid(row=2 * i, column=0, padx=5, pady=5)
                self["nl" + str(i)] = tkinter.Label(self["helper"], text="Notes", font=("Sans", 20))
                self["nl" + str(i)].grid(row=2 * i, column=1, padx=5, pady=5)
                self["e" + str(i)] = tkinter.Entry(self["helper"], font=("Sans", 20))
                self["e" + str(i)].grid(row=2 * i + 1, column=0, padx=5, pady=5)
                self["ne" + str(i)] = tkinter.Entry(self["helper"], font=("Sans", 20))
                self["ne" + str(i)].grid(row=2 * i + 1, column=1, padx=5, pady=5)
                if criteria in self.current_question.coding_done:
                    self["e" + str(i)].insert(0, self.current_question.coding_done[criteria].text)
                    self["ne" + str(i)].insert(0, self.current_question.coding_done[criteria].notes)
            self["previous"] = tkinter.Button(self.tk, text="< Previous", command=self.previous_question)
            self["previous"].grid(row=2, column=0, padx=5, pady=5, ipadx=15)
            self["next"] = tkinter.Button(self.tk, text="Next >", command=self.next_question)
            self["next"].grid(row=2, column=1, padx=5, pady=5, ipadx=15)
            self["next_new"] = tkinter.Button(self.tk, text="Next New >|", command=self.next_new_question)
            self["next_new"].grid(row=2, column=2, padx=5, pady=5, ipadx=15)

            self.logger.debug("Question shown")

    def next_question(self):
        self.__cleanup_answer_question()
        self.show_question("next")

    def previous_question(self):
        self.__cleanup_answer_question()
        self.show_question("previous")

    def next_new_question(self):
        self.__cleanup_answer_question()
        self.show_question("next_new")

    def __cleanup_answer_question(self):
        for element in self:
            if element[0] == "e":
                content = self[element].get()
                if content is "":
                    self[element].config(bg="#ffe0e0")
                else:
                    self[element].config(bg="#e0ffe0")
                    index = int(element[1:])
                    self.current_question.set_value(criteria=self.current_question.criterias[index],
                                                    value=content,
                                                    notes=self["ne{}".format(str(index))].get())

        for i in self:
            self[i].destroy()
        self.widgets = {}

    def run(self):
        self.logger.debug("Starting GUI")
        try:
            super(GUIPresenter, self).run()
            self.tk.mainloop()
        except Exception:
            self.logger.critical("Unhandled Error:\n{}".format(traceback.format_exc()).rstrip())
        else:
            self.logger.debug("Leaving GUI normally.")

    @staticmethod
    def focus_next_window(event):
        event.widget.tk_focusNext().focus()
        return "break"

    def feedback_file_correctness(self, filename):
        if os.path.isfile(filename):
            self["edata"].config(highlightbackground="GREEN")
            return True
        else:
            self["edata"].config(highlightbackground="RED")
        return False
