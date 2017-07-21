import os
from itertools import repeat
from itertools import takewhile
from sys import version_info
if version_info[0] == 2:
    from itertools import izip_longest as zip_longest
elif version_info[0] == 3:
    from itertools import zip_longest


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
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen)
