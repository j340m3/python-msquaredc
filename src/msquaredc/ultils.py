import os
import threading
import yaml

MULTITHREADING = True
lock = threading.Lock()


class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


def yaml_load(filename):
    try:
        with open(filename+".old", "r") as file:
            res = yaml.load(file)
            return res
    except FileNotFoundError:
        try:
            with open(filename, "r") as file:
                res = yaml.load(file)
                return res
        except FileNotFoundError:
            return None


def yaml_write(content, filename):
    rename = True
    try:
        os.rename(filename, filename+".old")
    except FileNotFoundError:
        rename = False
    try:
        with open(filename, "w+") as file:
            yaml.dump(content, file)
    except IOError:
        if rename:
            os.rename(filename+".old", filename)
    else:
        if rename:
            os.remove(filename+".old")
    print("finished")


@SingletonDecorator
class PersistableStack(object):
    def __init__(self, filename, multithreading=True):
        self.filename = filename
        self.thread = None
        self.values = None
        self.multithreading = multithreading

    def getValues(self):
        res = yaml_load(self.filename)
        if res is not None:
            self.values = res
        else:
            self.values = []

    def push(self, element):
        if not self.values:
            self.getValues()
        self.values.append(element)
        self.persist(yaml_write, self.values, self.filename)

    def pop(self):
        if not self.values:
            self.getValues()
        res = self.values.pop()
        self.persist(yaml_write, self.values, self.filename)
        return res

    def persist(self, func, *args):
        if self.multithreading:
            with lock:
                self.thread = threading.Thread(target=func, args=args)
                self.thread.daemon = True
                self.thread.start()
        else:
            func(*args)

    @property
    def count(self):
        return len(self.values)
