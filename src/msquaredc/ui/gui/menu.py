import tkinter

from msquaredc.ui.interfaces import AbstractMenu


class GUIMenu(AbstractMenu):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.root = parent
        while self.root.parent is not None:
            self.root = self.root.parent
        self.tk = self.parent.tk
        super(GUIMenu, self).__init__(self.parent, name)

        if not isinstance(self.parent, GUIMenu):
            self.menu = tkinter.Menu(self.tk, tearoff=False)
            self.tk.config(menu=self.menu)
        else:
            self.menu = tkinter.Menu(self.root.menu.tk, tearoff=False)

    def addEntry(self, entry, handle, *args, **kwargs):
        label = tkinter.StringVar(self.tk, entry, entry)
        super(GUIMenu, self).addEntry(entry, handle)
        self.root.add_label(entry, label.set)
        self.menu.add_command(label=label, command=handle)

    def addSeparator(self):
        self.menu.add_separator()

    def addSubmenu(self, entry, *args, **kwargs):
        super(GUIMenu, self).addSubmenu(entry)
        self.menu.add_cascade(label=entry.name, menu=entry.menu)
