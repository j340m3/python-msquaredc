# -*- coding: utf-8 -*-

import click


@click.command()
def main(args=None):  # pragma no cover
    """Console script for msquaredc"""
    gui = False
    if gui:
        from msquaredc.gui.main import main
        main()


if __name__ == "__main__":  # pragma no cover
    main()
