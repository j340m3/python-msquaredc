from zipfile import ZipFile


class Project(object):
    def __init__(self, *args, path=None, stack=None):
        # Project already exists
        if path is None:
            raise FileNotFoundError
        else:
            with ZipFile(path) as project_folder:
                with project_folder.open("state.yml") as state:
                    pass
        self.path = path
        self.stack = stack
