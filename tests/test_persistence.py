import os
import unittest

from msquaredc.persistence import BackedUpDict
from msquaredc.persistence import obtain
from msquaredc.persistence import persist


class TestPersistence(unittest.TestCase):
    def test_all(self):
        samples = [
            {"x": 1, "y": 2, "z": 3},
            {"x": 4, "y": 5, "z": ""},
        ]
        try:
            persist("test.txt", samples[0], "w+")
            persist("test.txt", samples[1], "a+")
            self.assertIn("test.txt", os.listdir(os.getcwd()))
            res = obtain("test.txt")
            # assert count("test.txt") == 3
        finally:
            if "test.txt" in os.listdir(os.getcwd()):
                os.remove("test.txt")

        self.assertEqual(len(res), len(samples))
        for i in range(len(samples)):
            for j in samples[i].keys():
                self.assertIn(j, res[i].keys())
                self.assertEqual(str(samples[i][j]), res[i][j], j + str(samples) + str(res))


class TestBackedUpDict(unittest.TestCase):
    def test_add(self):
        p = BackedUpDict(":memory:")
        p["bla"] = "blupp"
        self.assertEqual(p["bla"], "blupp")
        p[1] = 2
        self.assertEqual(p[1], 2)
        p[1] = "mahalo"
        self.assertEqual(p[1], "mahalo")
        self.assertIn(1, p.keys())
        self.assertIn("bla", p.keys())
        self.assertEqual(len(p), 2)
        p["1"] = "2"
        self.assertEqual(p[1], "mahalo")
