from sys import version_info
if version_info[0] == 2:
    # We are using Python 2.x
    import tkSimpleDialog as sdg
    import tkFileDialog as fdg
elif version_info[0] == 3:
    # We are using Python 3.x
    from tkinter import simpledialog as sdg
    from tkinter import filedialog as fdg


def NameDialog():  # pragma : no cover
    return sdg.askstring("Name dialog", "Please insert Name:")


def FileDialog():  # pragma : no cover
    return fdg.askopenfilename()
