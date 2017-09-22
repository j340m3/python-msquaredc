from msquaredc.persistence import BackedUpDict
import random
import yaml


class Project(object):
    def __init__(self, path=".", stack=None, *args, **kwargs):
        # Project already exists
        if path is None or len(path) == 0:
            raise FileNotFoundError
        else:
            self.state = BackedUpDict("{}/state".format(path))

        if "data" in self.state:
            with open("{}/{}".format(path, self.state["data"])) as data:
                self.data = self.handleTSV(data)
        else:
            if "data" in kwargs:
                with open(kwargs["data"]) as data:
                    self.data = self.handleTSV(data)
                self.state["data"] = kwargs["data"]
            else:
                raise FileNotFoundError("Data not Found.")

        if "questions" in self.state:
            self.questions = yaml.load(self.state["questions"])
        else:
            if "questions" in kwargs:
                self.questions = yaml.load(kwargs["questions"])
                self.state["questions"] = kwargs["questions"]
            else:
                raise FileNotFoundError

        self.init_dict(kwargs,seed=0,question_pos=0,questioned_pos=0)
        random.seed(self.state["seed"])
        self.randomstate = random.getstate()
        self.path = path
        self.stack = stack

    def init_dict(self,init_kwargs,**kwargs):
        for i in kwargs:
            if i not in self.state:
                if i in init_kwargs:
                    self.state[i] = init_kwargs[i]
                else:
                    self.state[i] = kwargs[i]

    @staticmethod
    def handleTSV(file):
        res = []
        titles = []
        for i,j in enumerate(file):
            if i == 0:
                titles = j.strip("\n").split("\t")
            else:
                res.append(dict(zip(titles,j.strip("\n").split("\t"))))
        return res

    @staticmethod
    def handleCSV(file):
        res =[]
        titles = []
        for i, j in enumerate(file):
            if i == 0:
                titles = j.split(",")
        print(titles)
        return res

    def __iter__(self):
        return self

    def __next__(self):J
		self.state[]
		
class FileNotFoundError(IOError):
    pass

