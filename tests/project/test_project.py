from msquaredc.project import Project
import unittest

class ProjectTest(unittest.TestCase):
    def test_init(self):
        p = Project(data="data sample for jerome.txt", questions="questions.yaml")
        print(p.state.keys())
