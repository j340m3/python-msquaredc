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
from __future__ import unicode_literals
import logging
import os
import click


from msquaredc.project import ProjectBuilder
from msquaredc.ui.interfaces import AbstractPresenter


@click.command()
@click.option('--config-file', default=None, help="Location of the project configuration file.")
@click.option("--data-file", default=None, help="Location of the data file.")
@click.option("--user-interface", default="gui", help="User interface to start. [tui | gui | web]")
@click.option("--separator", default="\t", help="Separator used in your file.")
@click.option("--loglevel", default="warning",
              help="On which level to log. [debug | info | warning | error | critical]")
@click.option("--logfile", default="logfile.log", help="Where to log.")
@click.option("--coder", default=None, help="Current coder.")
def main(config_file=None, data_file=None, user_interface="gui", separator="\t", loglevel="warning", logfile="logfile.log", coder=None):
    """Command line interface to msquaredc."""
    setup_logging(loglevel, logfile)
    presenter = None
    check_file(config_file)
    check_file(data_file)

    pb = ProjectBuilder(data=data_file, separator=separator, config=config_file, coder=coder)

    if user_interface == "gui":
        from msquaredc.ui.gui.presenter import GUIPresenter
        from msquaredc.ui.gui.menu import GUIMenu
        presenter = GUIPresenter(menuclass=GUIMenu, projectbuilder=pb)
    elif user_interface == "tui":
        from msquaredc.ui.tui.presenter import TUIPresenter
        from msquaredc.ui.tui.menu import TUIMenu
        presenter = TUIPresenter(menuclass=TUIMenu, projectbuilder=pb)
    elif user_interface == "web":
        print("NotSupportedYet")
        exit(0)
    else:
        presenter = AbstractPresenter(projectbuilder=pb)

    presenter.run()


def setup_logging(loglevel, logfile):
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
    if filename is None or not os.path.exists(filename):
        logging.log(logging.CRITICAL, "Couldn't find the file '{}'.".format(filename))
        import sys
        sys.exit(1)
    else:
        logging.log(logging.DEBUG, "Found the file '{}'.".format(filename))


if __name__ == "__main__":  # pragma no cover
    main()
