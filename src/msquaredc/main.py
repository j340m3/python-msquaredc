from msquaredc.ui.gui.core import MainFrame
from msquaredc.ui.gui.dialogs import NameDialog

from msquaredc.ui.gui.widgets import TrueFalseWidget

if __name__ == "__main__":
    widgets = [TrueFalseWidget("Has the question been answered?"),
               TrueFalseWidget("Is the answer correct?"), ]
    w = MainFrame(widgets)
    while w.user is None:
        w.user = NameDialog()
    w.start()
