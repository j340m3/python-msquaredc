import logging

from msquaredc.ui.interfaces import PresenterInterface


class Presenter(PresenterInterface):
    def __init__(self, *args, **kwargs):
        super(Presenter, self).__init__(*args, **kwargs)
        self.__logger = logging.getLogger(__class__.__name__)

    def new_project_wizard(self, path=None):
        self.__logger.info("Creating a new Project.")
        print(path)

    def load_mainframe(self, *args, **kwargs):
        self.__logger.info("Loading Mainframe.")
