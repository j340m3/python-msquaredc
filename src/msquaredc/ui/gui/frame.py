import tkinter


class CustomFrame(tkinter.Frame):
    def __init__(self, *args, **kwargs):
        super(CustomFrame, self).__init__(*args, **kwargs)
        self.bind("<Configure>", self.configure)
        self.drawn = []
        self.height = 0
        self.width = 0
        if "height" in kwargs:
            self.height = kwargs["height"]
        if "width" in kwargs:
            self.width = kwargs["width"]

    def configure(self, event):
        self.height = event.height
        self.width = event.width
        self.informHeight()

    def informHeight(self):
        pass

    def grid(self, *args, **kwargs):
        pass


class CustomLabel(tkinter.Frame):
    pass


if __name__ == '__main__':
    master = tkinter.Tk()
    i = CustomFrame(width=320, height=280)
    l1 = tkinter.Label(i, text="Blablabla")
    l1.grid()
    i.pack(fill=tkinter.BOTH, expand=1)
    tkinter.mainloop()
