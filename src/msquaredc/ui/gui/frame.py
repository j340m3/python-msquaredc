from sys import version_info

if version_info[0] == 2:
    # We are using Python 2.x
    import Tkinter as tk

elif version_info[0] == 3:
    # We are using Python 3.x
    import tkinter as tk


class CustomFrame(tk.Frame):
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


class CustomLabel(tk.Frame):
    pass


if __name__ == '__main__':
    master = tk.Tk()
    i = CustomFrame(width=320, height=280)
    l1 = tk.Label(i, text="Blablabla")
    l1.grid()
    i.pack(fill=tk.BOTH, expand=1)
    tk.mainloop()
