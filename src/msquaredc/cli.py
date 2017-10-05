"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mmsquaredc` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``msquaredc.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``msquaredc.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import logging

import click, os

from msquaredc.project import FileNotFoundError
from msquaredc.project import Project
from msquaredc.ui.interfaces import AbstractMenu
from msquaredc.ui.interfaces import AbstractPresenter


@click.command()
@click.option('--config-file', default=None, help="Location of the project configuration file.")
@click.option("--data-file", default="data.txt", help="Location of the data file.")
@click.option("--user-interface", default="gui", help="User interface to start. [tui | gui | web]")
@click.option("--loglevel", default="warning", help="On which level to log. [debug | info | warning | error | critical]")
@click.option("--logfile", default="logfile.log", help="Where to log.")
@click.option("--coder", default=None, help="Current coder.")
def main(config_file=None, data_file="data.txt", user_interface="gui", loglevel="warning", logfile="logfile.log",coder = None):
    """Command line interface to msquaredc."""
    setup_logging(loglevel,logfile)
    check_file(config_file)
    check_file(data_file)
    presenter = None
    if user_interface == "gui":
        from msquaredc.ui.gui.presenter import GUIPresenter
        from msquaredc.ui.gui.menu import GUIMenu
        presenter = GUIPresenter(menuclass=GUIMenu)
    elif user_interface == "tui":
        from msquaredc.ui.tui.presenter import TUIPresenter
        from msquaredc.ui.tui.menu import TUIMenu
        presenter = TUIPresenter(menuclass=TUIMenu)
    elif user_interface == "web":
        print("NotSupportedYet")
    else:
        presenter = AbstractPresenter()
    if config_file is None:
        project = presenter.new_project_wizard()
    else:
        try:
            #coder,disamb = presenter.getCoder()
            project = Project(data=data_file, questions=config_file, coder=coder)
        except FileNotFoundError:
            project = presenter.new_project_wizard(path=config_file, questions=config_file)
    presenter.load_mainframe(project)
    presenter.run()

def setup_logging(loglevel,logfile):
    translated = {"debug": logging.DEBUG,
                  "info": logging.INFO,
                  "warning": logging.WARNING,
                  "error": logging.ERROR,
                  "critical": logging.CRITICAL}
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-30s %(levelname)-8s %(message)s',
                        datefmt='%Y-%d-%m %H:%M:%S',
                        filename=logfile,
                        filemode="a")
    console = logging.StreamHandler()
    console.setLevel(translated.get(loglevel, logging.WARNING))
    formatter = logging.Formatter('%(name)-30s %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

def check_file(filename):
    if not os.path.exists(filename):
        logging.log(logging.CRITICAL,"Couldn't find the file '{}'.".format(filename))
        import sys
        sys.exit(1)
    else:
        logging.log(logging.DEBUG, "Found the file '{}'.".format(filename))

if __name__ == "__main__":  # pragma no cover
    main()
