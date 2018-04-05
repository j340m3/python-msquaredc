import os
import sqlite3
from itertools import repeat
from itertools import takewhile
from sys import version_info

if version_info[0] == 2:
    from itertools import izip_longest as zip_longest
elif version_info[0] == 3:
    from itertools import zip_longest


class BackedUpDict(object):
    def __init__(self, path):
        self.typemapping = {int: "int", str: "str", float: "float"}
        self.conn = sqlite3.connect(path)
        c = self.conn.cursor()
        for name, type_ in [("str", "text"), ("int", "integer"), ("float", "real")]:
            c.execute("""CREATE TABLE IF NOT EXISTS data_{}_str (key {}, value text);""".format(name, type_))
            c.execute("""CREATE TABLE IF NOT EXISTS data_{}_int (key {}, value integer);""".format(name, type_))
            c.execute("""CREATE TABLE IF NOT EXISTS data_{}_float (key {}, value real);""".format(name, type_))
        self.conn.commit()

    def __getitem__(self, item):
        c = self.conn.cursor()
        res = list()
        for i in ["str", "int", "float"]:
            c.execute("""SELECT value FROM data_{}_{} where key=?;""".format(self.typemapping[type(item)], i), (item,))
            res += c.fetchall()

        if len(res) == 1:
            return res[0][0]
        else:
            raise KeyError

    def get(self, item, default=None):
        try:
            res = self.__getitem__(item)
            return res
        except KeyError:
            return default

    def __setitem__(self, key, value):
        res = self.get(key, None)
        c = self.conn.cursor()
        if res is not None:
            c.execute("""DELETE FROM data_{}_{} WHERE key =?;""".format(self.typemapping[type(key)],
                                                                        self.typemapping[type(res)]), (key,))
        c.execute("""INSERT INTO data_{}_{} VALUES (?,?);""".format(self.typemapping[type(key)],
                                                                    self.typemapping[type(value)]), (key, value))
        self.conn.commit()

    def keys(self):
        c = self.conn.cursor()
        res = list()
        for i in ["str", "int", "float"]:
            for j in ["str", "int", "float"]:
                c.execute("""SELECT key FROM data_{}_{};""".format(i, j))
                res += c.fetchall()
        return [i[0] for i in res]

    def __len__(self):
        return len(self.keys())

    def __contains__(self, item):
        return item in self.keys()

    def __iter__(self):
        return iter(self.keys())


def obtain(filename):
    with open(filename, 'r') as file_:
        categories = []
        res = []
        for i, line in enumerate(file_):
            if i == 0:
                categories = list(map(str.strip, line.strip().split("\t")))
            else:
                res.append(dict(zip_longest(categories, map(str.strip, line.split("\t")), fillvalue="")))
    return res


def persist(filename, dict_, mode="a", split="\t"):
    order = None
    if filename in os.listdir(os.getcwd()):
        with open(filename) as file_:
            order = file_.readline().strip().split(split)
    with open(filename, mode) as file_:
        if order is None:
            order = list(dict_.keys())
            file_.write(split.join(order))
            file_.write("\n")
        file_.write(split.join([str(dict_[i]) for i in order]))
        file_.write("\n")


def count(filename):
    """Credits to Michael Bacon/Quentin Pradet from Stackoverflow

    filename -- Name of the file, of which the amount of lines shall be counted
    """
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen)
