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
        with open(filename + ".old", "r") as file:
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
        os.rename(filename, filename + ".old")
    except FileNotFoundError:
        rename = False
    try:
        with open(filename, "w+") as file:
            yaml.dump(content, file)
    except IOError:
        if rename:
            os.rename(filename + ".old", filename)
    else:
        if rename:
            os.remove(filename + ".old")
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


class Decorator:
    def __new__(self, *args, **kwargs):
        self.decoree = None
        self.newargs = args
        self.newkwargs = kwargs
        self.decorators = {}
        if "decorators" in self.newkwargs:
            self.decorators = self.newargs["decorators"]
        if args:
            if isinstance(args[0], type):
                self.decoree = args[0]
            if callable(args[0]):
                if len(args) == 1 and len(kwargs) == 0:
                    return args[0]
            else:
                pass
        return self

    def __init__(self, *args, **kwargs):
        self.decoree = None
        self.initargs = args
        self.initkwargs = kwargs
        if args and callable(args[0]):
            self.decoree = args[0]

    def __call__(self, *args, **kwargs):
        if args and callable(args[0]):
            self.decoree = args[0]
            if isinstance(self.decoree, type):
                return self.create_wrapping_class(self.decoree, self.decorators)
            return self.decoree
        elif self.decoree:
            if isinstance(self.decoree, type):
                return self.create_wrapping_class(args[0], self.decorators)(*args, **kwargs)
            return self.decoree(*args, **kwargs)

    @staticmethod
    def create_wrapping_class(cls, decorators):
        from six import with_metaclass

        class MetaNewClass(type):
            def __repr__(self):
                return repr(cls)

        class NewClass(with_metaclass(MetaNewClass, cls)):
            def __init__(self, *args, **kwargs):
                self.__instance = cls(*args, **kwargs)
            "This is the overwritten class"
            def __getattribute__(self, attr_name):
                if attr_name == "__class__":
                    return cls
                obj = super(NewClass, self).__getattribute__(attr_name)
                if hasattr(obj, '__call__'):
                    if attr_name in decorators:
                        for decorator in decorators:
                            obj = decorator(obj)
                    elif "*" in decorators:
                        for decorator in decorators:
                            obj = decorator(obj)
                    return obj
                return obj

            def __repr__(self):
                return repr(self.__instance)
        return NewClass


def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return result
