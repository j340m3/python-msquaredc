=====
Usage
=====

Command line interface
----------------------

To launch M²C from the command line, simply type:

    ``msquaredc``

In order to save yourself typing work, you may also pass several options:

``--config-file``
    The YAML-File containing the configurations of the project.

``--data-file``
    The CSV-File (with ``;`` as separator), where all the data to process is stored.

``--user-interface``
    **Upcoming feature. NOT ready for usage yet!** Choose your user interface.

    - *gui*: Graphical user interface based on Tkinter (default)
    - *tui*: Text-only user interface based on urwid (not there at all)
    - *web*: Webbased user interface (website) based on Flask/Django (not there at all)

``--loglevel``
    Verbosiness of the console. In parallel,
    all events will be logged on highest verbosity levelinto the file ``logfile.log``.
    The options are (from silent to loud):

    - critical
    - error
    - warning
    - info
    - debug

``--logfile``
    As mentioned above, msquaredc loggs all event into a file (e.g. ``logfile.log``).
    You can use this option to pass a different filename.

``--coder``
    Tell msquaredc who's the boss right now. :)
