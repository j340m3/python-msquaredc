from sys import version_info
if version_info[0] == 2:
    # We are using Python 2.x
    import Tkinter as tk
elif version_info[0] == 3:
    # We are using Python 3.x
    import tkinter as tk


class Paper(tk.Frame):  # pragma : no cover
    def __init__(self, master, coding, data):
        super(Paper, self).__init__(master)


if __name__ == "__main__":
    Paper("config.yml", None)
