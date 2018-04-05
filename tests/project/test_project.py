import os
import unittest

from msquaredc.project import Project


class PermissionError(IOError):
    pass

class FileNotFoundError(IOError):
    pass

class WindowsError(IOError):
    pass

def cleanup(func):
    def call(*args,**kwargs):
        try:
            if os.path.isfile(func.__name__):
                os.remove(func.__name__)
        except (PermissionError,FileNotFoundError,WindowsError) as e:
            pass
        try:
            res = func(*args, file=func.__name__,**kwargs)
        finally:
            try:
                if os.path.isfile(func.__name__):
                    os.remove(func.__name__)
            except (PermissionError, FileNotFoundError,WindowsError) as e:
                pass
        return res
    return call


class ProjectTest(unittest.TestCase):
    pass
"""    
    @cleanup
    def test_init(self,file):
        p = Project(data="data.txt", questions="config.yml", coder="MGM", file=file)

    @cleanup
    def test_integration(self,file):
        p = Project(data="data.txt", questions="config.yml", coder="MGM", file=file)
        value = 0
        for index,i in enumerate(p):
            for j in i.coding_questions:
                i[j] = value
                value += 1
        p.export()
"""
