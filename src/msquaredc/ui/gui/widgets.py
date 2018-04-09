import tkinter


class MyWidget:  # pragma : no cover
    def __init__(self, label):
        self.label = label


class TrueFalseWidget(MyWidget):  # pragma : no cover
    def __init__(self, label):
        super(TrueFalseWidget, self).__init__(label)
        self.widget = None
        self.labelw = None

    def draw(self, root, line):
        self.widget = tkinter.Checkbutton(root)
        self.widget.grid(column=1, row=line, sticky=tkinter.NSEW)
        self.labelw = tkinter.Label(root, text=self.label, justify=tkinter.LEFT)
        self.labelw.grid(column=2, row=line, sticky=tkinter.NSEW)


class ScaleWidget(tkinter.Frame):  # pragma : no cover
    def __init__(self, master, label, min_, max_, redundancy=0):
        super(ScaleWidget, self).__init__(master)
        self.min = min_
        self.max = max_
        self.variables = [tkinter.Entry(master, width=2) for _ in range(redundancy + 1)]
        self.label = tkinter.Label(master, text=label)
