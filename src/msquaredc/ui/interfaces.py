import abc
import gettext
import logging

gettext.bindtextdomain("msquaredc", ".")
gettext.textdomain("msquaredc")
_ = gettext.gettext


# logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',level=logging.DEBUG)

class AbstractMenu:
    __metaclass__ = abc.ABCMeta

    def __init__(self, main, name, logger=None):
        if logger:
            self.logger = logging.getLogger(logger)
        else:
            self.logger = logging.getLogger("Menu")
        self.name = name
        self.main = main
        self.entries = []

    def addEntry(self, entry, handle, *args, **kwargs):
        self.entries.append((entry, handle))
        self.logger.info("Adding Entry {} to menu {} ".format(entry, self.name))

    def addSubmenu(self, menu, *args, **kwargs):
        self.entries.append((menu.name, menu.entries))
        self.logger.info("Adding Submenu {} to menu {} ".format(menu.name, self.name))

    def getLabel(self):
        pass


class AbstractLabel:
    __metaclass__ = abc.ABCMeta

    def __init__(self, text):
        self.text = text


class AbstractPresenter:
    __metaclass__ = abc.ABCMeta

    def __init__(self, name=None, menuclass=AbstractMenu, *args, **kwargs):
        if name:
            self.logger = logging.getLogger(name)
        else:
            self.logger = logging.getLogger(__name__)

        self._menuclass = menuclass
        self.labels = {}

        # Init Menu
        self.menu = menuclass(self, _("File"))
        submenu = menuclass(self.menu, _("Title1"))
        submenu.addEntry("Entry", None)
        self.menu.addSubmenu(submenu)
        submenu2 = menuclass(self.menu, "Title2")
        submenu2.addEntry("Entry2", None)
        submenu2.addEntry("Entry3", None)
        self.menu.addSubmenu(submenu2)

    def add_label(self, key, callable_f):
        self.labels[key] = self.labels.get(key, []).append(callable_f)

    def update_labels(self):
        for key in self.labels:
            for callable_f in self.labels[key]:
                callable_f()

    def info(self, msg, *args, **kwargs):
        self.logger.log(logging.INFO, "Informing user with: " + str(msg), *args, **kwargs)

    def handle(self, event, *args, **kwargs):
        self.logger.log(logging.INFO, "Handling event : " + str(event), *args, **kwargs)

    def set_ui_element(self, ui_element, msg, *args, **kwargs):
        self.logger.log(logging.INFO,
                        "Tried to set an UI-Element of the Interface, probably the child class hasn't implemented it yet!")

    def new_project_wizard(self, path=None):
        self.logger.log(logging.ERROR,
                        "Tried to start the Project Wizard from the Interface, probably the child class hasn't implemented it yet!")

    def load_mainframe(self, *args, **kwargs):
        self.logger.log(logging.ERROR,
                        "Tried to load the Mainframe from the Interface, probably the child class hasn't implemented it yet!")

    def show_settings(self, *args, **kwargs):
        self.logger.log(logging.ERROR,
                        "Tried to show the settings pane from the Interface, probably the child class hasn't implemented it yet!")

    def run(self):
        self.logger.log(logging.ERROR,
                        "Tried to run the User Interface from the Interface, probably the child class hasn't implemented it yet!")
