from zipfile import ZipFile


class Project(object):
    def __init__(self, path=None, stack=None, *args):

        # Project already exists
        if path is None or len(path) == 0:
            raise FileNotFoundError
        else:
            with ZipFile(path) as project_folder:
                with project_folder.open("state.yml") as state:
                    state.read()
        self.path = path
        self.stack = stack


class FileNotFoundError(IOError):
    pass
