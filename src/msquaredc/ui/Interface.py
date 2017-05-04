import abc
import logging


class Interface:
    __metaclass__ = abc.ABCMeta

    def __init__(self, logger=logging.getLogger(__name__)):
        self.logger = logger

    def info(self, msg, *args, **kwargs):
        self.logger.log(logging.INFO, "Informing user with: " + str(msg), *args, **kwargs)

    def handle(self, event, *args, **kwargs):
        self.logger.log(logging.INFO, "Handling event : " + str(event), *args, **kwargs)

    def set_ui_element(self, ui_element, msg, *args, **kwargs):
        pass
