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

import click

from msquaredc.project import FileNotFoundError
from msquaredc.project import Project
from msquaredc.ui.interfaces import AbstractMenu
from msquaredc.ui.interfaces import AbstractPresenter


@click.command()
@click.option('--project-file', default="", help="Location of the project file")
@click.option("--user-interface", default="gui", help="User interface to start. [tui|gui|web]")
def main(project_file, user_interface):
    """Console script for msquaredc"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    presenter = AbstractPresenter(menuclass=AbstractMenu)
    if user_interface == "gui":
        from msquaredc.ui.gui.presenter import GUIPresenter, GUIMenu
        presenter = GUIPresenter(menuclass=GUIMenu)
    elif user_interface == "tui":
        from msquaredc.ui.tui.presenter import TUIPresenter, TUIMenu
        presenter = TUIPresenter(menuclass=TUIMenu)
    elif user_interface == "web":
        print("NotSupportedYet")
    else:
        presenter = AbstractPresenter()
    if project_file is None:
        project = presenter.new_project_wizard()
    else:
        try:
            project = Project(path=project_file)
        except FileNotFoundError:
            project = presenter.new_project_wizard(path=project_file)
    presenter.load_mainframe(project)
    presenter.run()


if __name__ == "__main__":  # pragma no cover
    main()
