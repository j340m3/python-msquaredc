from sys import version_info

from msquaredc.ui.interfaces import AbstractMenu

if version_info[0] == 2:
    # We are using Python 2.x
    import Tkinter as tk
elif version_info[0] == 3:
    # We are using Python 3.x
    import tkinter as tk


class GUIMenu(AbstractMenu):
    def __init__(self, root, name):
        self.tk = root.tk
        self.root = root
        super(GUIMenu, self).__init__(root, name)

        if not isinstance(root, GUIMenu):
            self.menu = tk.Menu(self.tk, tearoff=False)
            self.tk.config(menu=self.menu)
        else:
            self.menu = tk.Menu(self.root.menu, tearoff=False)

    def addEntry(self, entry, handle, *args, **kwargs):
        super(GUIMenu, self).addEntry(entry, handle)
        self.menu.add_command(label=entry, command=handle)

    def addSeparator(self):
        self.menu.add_separator()

    def addSubmenu(self, entry, *args, **kwargs):
        super(GUIMenu, self).addSubmenu(entry)
        self.menu.add_cascade(label=entry.name, menu=entry.menu)
