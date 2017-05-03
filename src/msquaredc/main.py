from msquaredc.gui.core import MainFrame
from msquaredc.gui.widgets import TrueFalseWidget
from msquaredc.gui.dialogs import NameDialog
from msquaredc.gui.dialogs import FileDialog
from msquaredc.persistence import open_file
import PyYAML


if __name__ == "__main__":


    widgets = [TrueFalseWidget("Has the question been answered?"),
           TrueFalseWidget("Is the answer correct?"), ]
    w = MainFrame(widgets)
    while w.user is None:
        w.user = NameDialog()
    w.start()
