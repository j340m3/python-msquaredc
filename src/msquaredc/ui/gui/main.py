from sys import version_info

from msquaredc.ui.gui.core import MainApplication

if version_info[0] == 2:
    # We are using Python 2.x
    import Tkinter as tk
elif version_info[0] == 3:
    # We are using Python 3.x
    import tkinter as tk


def main():
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.geometry("640x480")
    root.mainloop()
