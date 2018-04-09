import logging
import os
import tkinter
import tkinter.filedialog

import yaml

from msquaredc import persistence
from msquaredc import utils
from msquaredc.ui.gui.widgets import ScaleWidget


class MainFrame(object):  # pragma no cover
    def __init__(self, widgets):
        self.widgets = widgets
        self.tk = tkinter.Tk()
        self.tk.title("msquaredc")
        self.q = self.a = None
        self.__is_fullscreen = False
        self.frame = tkinter.Frame(self.tk)
        self.frame.grid(row=0, column=0)
        self.init_keybindings()
        self.init_menubar()
        self.init_content()
        self.open_files = {"save": None, "open": None}
        self.__input = None
        self.showResults("<No file loaded!>", "<Please open a file!>")
        self.act = None
        self.prev = []
        self.user = None

    def init(self):
        # Show NameDialog
        # validate output
        # draw gui
        pass

    def init_menubar(self):
        menubar = tkinter.Menu(self.tk)
        self.tk.config(menu=menubar)

        fileMenu = tkinter.Menu(menubar)

        fileMenu.add_command(label="Open", command=persistence.open_file)
        fileMenu.add_command(label="Save", command=self.save_file)

        fileMenu.add_separator()

        fileMenu.add_command(label="Exit", underline=0, command=self.onExit)
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)

    def showResults(self, q, a):
        self.q = tkinter.Label(self.tk, text=q)
        self.q.grid(column=2, row=1, sticky=tkinter.NSEW, columnspan=1)
        self.a = tkinter.Label(self.tk, text=a)
        self.a.grid(column=2, row=2, sticky=tkinter.NSEW, columnspan=1)

    def init_content(self):
        for i, j in enumerate(self.widgets):
            j.draw(self.tk, i + 3)
        self.tk.grid_rowconfigure(0, weight=1)
        self.tk.grid_rowconfigure(len(self.widgets) + 3, weight=1)
        self.tk.grid_columnconfigure(0, weight=1)
        self.tk.grid_columnconfigure(len(self.widgets) + 3, weight=1)

    def init_keybindings(self):
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.__is_fullscreen = not self.__is_fullscreen  # Just toggling the boolean
        self.tk.attributes('-fullscreen', self.__is_fullscreen)
        self.tk.overrideredirect(self.__is_fullscreen)
        return "break"

    def end_fullscreen(self, event=None):
        self.__is_fullscreen = False
        self.tk.attributes("-fullscreen", False)
        self.tk.overrideredirect(False)
        return "break"

    def save_file(self):
        filename = tkinter.filedialog.asksaveasfilename()
        try:
            file = open(filename, 'w')
            self.open_files["save"].append(file)
        except FileNotFoundError:
            pass

    def onExit(self):
        for category in self.open_files:
            self.open_files[category].close()
        self.tk.quit()

    def start(self):
        self.tk.mainloop()


class MainApplication(tkinter.Frame):  # pragma no cover
    def __init__(self, parent, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.callbacks = {}
        self.statusbar = StatusBar(self)
        self.toolbar = ToolBar(parent, self)
        self.navbar = NavBar(self)
        self.main = Main(self, "config.yml", "jerome.txt")

        self.statusbar.pack(side="bottom", fill="x")
        # self.toolbar.pack(side="top", fill="x")
        self.navbar.pack(side="bottom", anchor="se")
        self.main.pack(side="top", expand=True)  # fill removed

    def add_callback(self, name, function):
        callbacks = self.get_callbacks(name)
        callbacks.append(function)
        self.callbacks[name] = callbacks

    def get_callbacks(self, name):
        return self.callbacks.get(name, [])

    def handle_callback(self, name):
        if self.get_callbacks(name):
            for i in self.get_callbacks(name):
                i()
        else:
            self.notice("".join(["The event ", name, " has been unhandled!"]))

    def notice(self, string):
        logging.log(logging.INFO, string)
        self.statusbar.variable.set(string)


class StatusBar(tkinter.Frame):  # pragma no cover
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)
        self.variable = tkinter.StringVar()
        self.label = tkinter.Label(self, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W,
                                   textvariable=self.variable,
                                   font=('arial', 10, 'normal'))
        self.variable.set('Status Bar')
        self.label.pack(fill=tkinter.X)


class NavBar(tkinter.Frame):  # pragma no cover
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)
        self.next = tkinter.Button(text="Next >", command=lambda: master.handle_callback("next"))
        self.prev = tkinter.Button(text="< Previous", command=lambda: master.handle_callback("prev"))
        self.prev.grid(column=0, row=0, in_=self, pady=5)
        self.next.grid(column=1, row=0, in_=self, padx=5, pady=5)


class ToolBar(tkinter.Menu):  # pragma no cover
    def __init__(self, master, handler):
        tkinter.Menu.__init__(self, master)
        master.config(menu=self)

        fileMenu = tkinter.Menu(self, tearoff=False)

        fileMenu.add_command(label="Open", command=lambda: handler.handle_callback("open"))
        fileMenu.add_command(label="Save", command=lambda: handler.handle_callback("save"))

        fileMenu.add_separator()

        fileMenu.add_command(label="Exit", underline=0, command=lambda: handler.handle_callback("exit"))
        self.add_cascade(label="File", underline=0, menu=fileMenu)


class Main(tkinter.Frame):  # pragma no cover
    def __init__(self, master, paper, data):
        tkinter.Frame.__init__(self, master)
        master.add_callback("next", lambda: Main.get_next(self))
        self.master = master
        # Get paper information
        ci = None
        with open(paper) as stream:
            ci = yaml.load(stream)
        self.questions = ci["questions"]
        self.title = ci["title"]
        self.order = ci["order"]
        self.show = ci["show"]
        self.user = ci["user"]

        # Get Data
        self.data = persistence.obtain(data)

        self.infofield = InfoField(self)
        self.infofield.grid(row=0)
        self.infofield.title = self.title
        self.widgetfield = WidgetField(self, {})

        self.current_question_index = 0
        self.current_answerer_index = 0
        self.start()

    def run(self):
        questions = [i["text"] for i in self.questions]
        for i, question in enumerate(self.questions):
            # Collect answers to code
            # coded = []
            if "out{}.txt".format(i) in os.listdir(os.getcwd()):
                # coded = persistence.obtain("out{}.txt".format(i))
                pass
            for answerer in self.data:
                for column in answerer:
                    if column not in questions:
                        pass

    def start(self):
        # Pick question + solution

        # Build and display
        self.infofield.question = self.questions[self.current_question_index]["text"]
        self.infofield.answer = self.data[self.current_answerer_index][self.infofield.question]

        self.widgetfield = WidgetField(self, self.questions[self.current_question_index]["coding"])
        self.widgetfield.show()
        self.widgetfield.grid(row=1)

    def get_next(self):
        # store previous
        used = [i["text"] for i in self.questions]
        sample = {i: self.data[self.current_answerer_index][i] for i in self.data[self.current_answerer_index]
                  if i not in used}
        sample["question"] = self.questions[self.current_question_index]["text"]

        sample.update(self.widgetfield.get_res_dict())
        print(sample)
        persistence.persist("out{}.txt".format(self.current_question_index), sample, "a+")

        self.current_answerer_index += 1
        if self.current_answerer_index >= len(self.data):
            self.current_answerer_index = 0
            self.current_question_index += 1
        # Check for resumables

        if self.current_question_index >= len(self.questions):
            self.infofield.question = "Finished"
            self.infofield.answer = "You may now leave"
        else:
            self.infofield.question = self.questions[self.current_question_index]["text"]
            if self.infofield.question in self.data[self.current_answerer_index]:
                self.infofield.answer = self.data[self.current_answerer_index][self.infofield.question]
            else:
                best = -1
                element = None
                for i in self.data[self.current_answerer_index]:
                    res = utils.lcs(i, self.infofield.question)
                    if len(res) > best:
                        element = i
                        best = len(res)
                self.infofield.answer = self.data[self.current_answerer_index][element]
            self.widgetfield.grid_forget()
            self.widgetfield.destroy()
            self.widgetfield = WidgetField(self, self.questions[self.current_question_index]["coding"])
            self.widgetfield.show()
            self.widgetfield.grid(row=1)


class InfoField(tkinter.Frame):  # pragma no cover
    def __init__(self, master):
        font = ("serif", 16)
        tkinter.Frame.__init__(self, master)
        self.__titlevar = tkinter.StringVar(self, "Title")
        self.__title = tkinter.Label(master, textvariable=self.__titlevar, font=("Helvetica", 18), pady=10)
        self.__questionvar = tkinter.StringVar(self, "Question")
        self.__question = tkinter.Label(master, textvariable=self.__questionvar, anchor=tkinter.W,
                                        font=("serif", 16, "bold"),
                                        pady=5)
        self.__answervar = tkinter.StringVar(self, "Answer")
        self.__answer = tkinter.Label(master, textvariable=self.__answervar, anchor=tkinter.W, font=("Times", 16),
                                      pady=5,
                                      relief="groove")
        self.__lengthvar = tkinter.StringVar(self, "Length")
        self.__length = tkinter.Label(master, textvariable=self.__lengthvar, anchor=tkinter.W, font=font, pady=5)
        self.q = tkinter.Label(self, text="Question:", anchor=tkinter.E, font=font, pady=5)
        self.a = tkinter.Label(self, text="Answer:", anchor=tkinter.E, font=font, pady=10)
        self.length_label = tkinter.Label(self, text="Length:", anchor=tkinter.E, font=font, pady=5)
        self.__title.grid(in_=self, row=0, columnspan=2)
        self.q.grid(in_=self, column=0, row=1)
        self.__question.grid(in_=self, column=1, row=1)
        self.a.grid(in_=self, column=0, row=2)
        self.__answer.grid(in_=self, column=1, row=2)
        # self.l.grid(in_=self,column=0,row=3)
        # self.__length.grid(in_=self,column=1,row=3)

    @property
    def title(self):
        return self.__titlevar.get()

    @title.setter
    def title(self, value):
        self.__titlevar.set(value)

    @property
    def question(self):
        return self.__questionvar.get()

    @question.setter
    def question(self, value):
        self.__questionvar.set(value)

    @property
    def answer(self):
        return self.__answervar.get()

    @answer.setter
    def answer(self, value):
        self.__answervar.set(value)
        self.__lengthvar.set(" ".join(["Symbols", str(len(self.answer)), "Words", str(len(self.answer.split(" ")))]))

    @property
    def length(self):
        return self.__lengthvar.get()

    @length.setter
    def length(self, value):
        self.__lengthvar.set(value)


class WidgetField(tkinter.Frame):  # pragma no cover
    def __init__(self, master, criterias):
        tkinter.Frame.__init__(self, master)
        self.criterias = criterias
        self.widgets = []
        for i in criterias:
            self.widgets.append(ScaleWidget(master, i["criteria"], i["min"], i["max"]))

    def show(self):
        for i, element in enumerate(self.widgets):
            element.variables[0].grid(column=0, row=i, in_=self)
        for i, element in enumerate(self.widgets):
            element.label.grid(column=1, row=i, in_=self)
        for i, element in enumerate(self.widgets):
            index = 2
            for k, j in enumerate(element.variables[1:]):
                j.grid(column=index + k, row=i, in_=self)

    def get_res_dict(self):
        return {element.label.cget('text'): element.variables[0].get() for element in self.widgets}
