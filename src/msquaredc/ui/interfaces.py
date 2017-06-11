import abc
import logging


class PresenterInterface:
    __metaclass__ = abc.ABCMeta

    def __init__(self, logger=logging.getLogger(__name__)):
        self.logger = logger

    def info(self, msg, *args, **kwargs):
        self.logger.log(logging.INFO, "Informing user with: " + str(msg), *args, **kwargs)

    def handle(self, event, *args, **kwargs):
        self.logger.log(logging.INFO, "Handling event : " + str(event), *args, **kwargs)

    def set_ui_element(self, ui_element, msg, *args, **kwargs):
        self.logger.log(logging.ERROR,
                        "Tried to set an UI-Element of the Interface, probably the child class hasn't implemented it yet!")

    def new_project_wizard(self, path=None):
        self.logger.log(logging.ERROR,
                        "Tried to start the Project Wizard from the Interface, probably the child class hasn't implemented it yet!")

    def load_mainframe(self, *args, **kwargs):
        self.logger.log(logging.ERROR,
                        "Tried to load the Mainframe from the Interface, probably the child class hasn't implemented it yet!")
