from msquaredc.ui.interfaces import AbstractPresenter


class TUIAbstractPresenter(AbstractPresenter):
    def __init__(self, *args, **kwargs):
        super(TUIAbstractPresenter, self).__init__(__name__, *args, **kwargs)

    def new_project_wizard(self, path=None):
        self.logger.info("Creating a new Project.")

    def load_mainframe(self, *args, **kwargs):
        self.logger.info("Loading Mainframe.")
