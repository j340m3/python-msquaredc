import tkinter.simpledialog


def NameDialog():  # pragma : no cover
    return tkinter.simpledialog.askstring("Name dialog", "Please insert Name:")


def FileDialog():  # pragma : no cover
    return tkinter.filedialog.askopenfilename()
