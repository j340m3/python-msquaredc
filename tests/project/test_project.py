from msquaredc.project import Project
import unittest,os

class PermissionError(IOError):
    pass

class FileNotFoundError(IOError):
    pass

class WindowsError(IOError):
    pass

def test_cleanup(func):
    def call(*args,**kwargs):
        try:
            os.remove(func.__name__)
        except (PermissionError,FileNotFoundError,WindowsError):
            pass
        try:
            res = func(*args, file=func.__name__,**kwargs)
        finally:
            try:
                os.remove(func.__name__)
            except (PermissionError, FileNotFoundError,WindowsError):
                pass
        return res
    return call


class ProjectTest(unittest.TestCase):
    @test_cleanup
    def test_init(self,file):
        p = Project(data="data sample for jerome.txt", questions="config.yml", coder="MGM", file=file)

    @test_cleanup
    def test_integration(self,file):
        p = Project(data="data sample for jerome.txt", questions="config.yml", coder="MGM", file=file)
        value = 0
        for index,i in enumerate(p):
            for j in i.coding_questions:
                i[j] = value
                value += 1
        p.export()
