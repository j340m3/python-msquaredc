import os
import random
import sqlite3
from builtins import str
import yaml


class FileNotFoundError(IOError):
    pass


class ProjectBuilder(object):
    def __init__(self, **kwargs):
        if "data" in kwargs:
            self.data = kwargs["data"]
        else:
            self.data = None
        if "coder" in kwargs:
            self.coder = kwargs["coder"]
        else:
            self.coder = None
        if "config" in kwargs:
            self.config = kwargs["config"]
        else:
            self.config = None
        if "separator" in kwargs:
            self.separator = kwargs["separator"]
        else:
            self.separator = None

    def finished(self):
        return self.data is not None and self.coder is not None and self.config is not None

    def build(self):
        return Project(data=self.data, coder=self.coder, config=self.config, separator=self.separator)


class Project(object):
    def __init__(self, path=".", file="project.db", coder=None, *args, **kwargs):
        # Project file doesn't already exist
        self.path = path
        self.file = file
        self.conn = sqlite3.connect(os.path.join(path, file))
        self.init_db(path, *args, **kwargs)
        self.current_coding_unit = None
        if coder is not None:
            self.coder = coder
        else:
            raise Exception("Please define the coder!")

    def init_db(self, path, *args, **kwargs):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS vars (key text, value text)""")
        c.execute("""CREATE TABLE IF NOT EXISTS translation (clear text, translated text, UNIQUE(clear, translated))""")
        self.conn.commit()
        if "data" in kwargs:
            with open(os.path.join(path, kwargs["data"])) as file:
                res = Project.handleCSV(file, kwargs["separator"])
            if len(res):
                titles = list(res[0].keys())
                cquery = ["{} {}".format(self.__transform_column(i), "TEXT") for i in titles]
                cquery = ", ".join(cquery)
                c.execute("""CREATE TABLE IF NOT EXISTS individuals (id INTEGER PRIMARY KEY,{})""".format(cquery))
                self.conn.commit()
                for row in res:
                    columns = []
                    values = []
                    for column in row:
                        if len(row[column].strip()) != 0:
                            columns.append(self.__transform_column(column))
                            values.append((row[column]))
                    aquery = " AND ".join(i + "=?" for i in columns)

                    if len(values):
                        c.execute("""SELECT id FROM individuals WHERE {}""".format(aquery), values)
                        identifier = c.fetchone()
                        if not identifier:
                            c.execute("""INSERT INTO individuals ({}) VALUES ({})""".format(", ".join(columns),
                                                                                            " ,".join(
                                                                                                "?" for _ in values)),
                                      values)
                            self.conn.commit()
        if "config" in kwargs:
            c.execute("""CREATE TABLE IF NOT EXISTS question_assoc (question text, coding text)""")
            with open(os.path.join(path, kwargs["config"])) as file:
                questions = yaml.load(file)
                if questions is None:
                    raise Exception("Could not read the Config file!")
            for question in questions["questions"]:
                qquery = ", ".join(
                    [self.__transform_column(i["criteria"]) + " TEXT" for i in question["coding"]] + ["coder TEXT"])
                c.execute("""CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, {})""".format(
                    self.__transform_column(question["text"]), qquery))
                for i in question["coding"]:
                    c.execute("""INSERT INTO question_assoc SELECT ?,?
                                  WHERE NOT EXISTS(SELECT 1 FROM question_assoc WHERE question=? AND coding=?)""",
                              (question["text"], i["criteria"], question["text"], i["criteria"]))
                self.conn.commit()

    def get_questions(self, question):
        c = self.conn.cursor()
        c.execute("""SELECT coding FROM question_assoc WHERE question=?""", (question,))
        res = [i[0] for i in c.fetchall()]
        return res

    def __transform_column(self, column):
        column = column.strip()
        before = column
        for i in "?()-,;[].=":
            column = column.replace(i, "_")
        columns = column.split(" ")
        columns = [column.lower() for column in columns]
        kw = ["alter", "group"]
        for i in range(len(columns)):
            if columns[i] in kw:
                columns[i] = "_".join([columns[i][:-1], columns[i][-1]])
        column = "_".join(columns)
        c = self.conn.cursor()
        c.execute("""INSERT OR IGNORE INTO translation (clear, translated) VALUES (?,?)""", (before, column))
        self.conn.commit()
        return column

    def __reverse_transform_column(self, column):
        c = self.conn.cursor()
        c.execute("""SELECT clear FROM translation WHERE translated=?""", (column,))
        res = c.fetchone()
        if res is not None and len(res) > 0:
            return str(res[0])
        return str(None)

    """
    def init_dict(self, init_kwargs, **kwargs):
        for i in kwargs:
            if i not in self.state:
                if i in init_kwargs:
                    self.state[i] = init_kwargs[i]
                else:
                    self.state[i] = kwargs[i]
    """
    @staticmethod
    def handleCSV(file, separator):
        res = []
        titles = []
        for i, j in enumerate(file):
            if i == 0:
                titles = j.strip("\n").split(separator)
            else:
                res.append(dict(zip(titles, j.strip("\n").split(separator))))
        return res

    @property
    def all_tables(self):
        c = self.conn.cursor()
        c.execute("""SELECT name FROM sqlite_master WHERE type='table'""")
        return [self.__transform_column(i[0]) for i in c.fetchall()]

    @property
    def custom_tables(self):
        return [i for i in self.all_tables if i not in self.system_tables]

    @property
    def system_tables(self):
        return ["vars", "individuals", "question_assoc", "translation"]

    def get_columns(self, table):
        c = self.conn.cursor()
        c.execute("""PRAGMA table_info({})""".format(table))
        return [i[1] for i in c.fetchall()]

    def get_number_of_entries(self, table):
        c = self.conn.cursor()
        c.execute("""SELECT count(*) FROM individuals""".format(self.__transform_column(table)))
        return c.fetchall()[0][0]

    def get_whole_table(self, table):
        colums = self.get_columns(table)
        c = self.conn.cursor()
        c.execute("""SELECT {} FROM {}""".format(", ".join(colums), table))
        return c.fetchall()

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_coding_unit is not None:
            if not self.current_coding_unit.isFinished():
                return self.current_coding_unit
        amount_of_individuals = self.get_number_of_entries("individuals")
        for table in self.custom_tables:
            c = self.conn.cursor()
            c.execute("""SELECT * FROM {}""".format(table))

            ids_in_table = c.fetchall()
            ids_in_table[:] = [i for i in ids_in_table if None not in i]
            if amount_of_individuals > len(ids_in_table):
                entries = set(range(amount_of_individuals)) - set([i[0] for i in ids_in_table])
                entry = random.choice(list(entries))
                c.execute("""SELECT {} FROM individuals""".format(table))
                coding_answer = c.fetchall()[entry][0]
                coding_question = self.__reverse_transform_column(table)
                questions = self.get_questions(coding_question)
                questions[:] = [i for i in questions if not self.__question_already_answered(coding_question, i, entry)]
                if len(questions) == 0:
                    c.execute("""SELECT * FROM question_assoc""")
                    res = c.fetchall()
                    for i in res:
                        print(i, len(i[0]), len(coding_question), repr(coding_question))
                    raise Exception("This should not happen")
                self.current_coding_unit = CodingUnit(self, coding_question, coding_answer, questions, entry)
                return self.current_coding_unit
        raise StopIteration

    def __question_already_answered(self, coding_question, question, id_):
        c = self.conn.cursor()
        c.execute("""SELECT {} FROM {} WHERE id=?""".format(self.__transform_column(question),
                                                            self.__transform_column(coding_question)), (id_,))
        res = c.fetchone()
        return res is not None and res[0] is not None

    def store_answer(self, coding_question, question, answer, id_):
        c = self.conn.cursor()
        c.execute("""INSERT OR IGNORE INTO {} (id,{}) VALUES (?,?)""".format(self.__transform_column(coding_question),
                                                                             self.__transform_column(question)),
                  (id_, answer))
        c.execute("""UPDATE {} SET id=?,{}=? WHERE id=?""".format(self.__transform_column(coding_question),
                                                                  self.__transform_column(question)),
                  (id_, answer, id_))
        self.conn.commit()

    def export(self, filename="out.txt"):
        with open(os.path.join(self.path, filename), "w") as file:
            file.write("\t".join([self.__reverse_transform_column(i) for i in self.get_columns("individuals") if
                                  i not in self.custom_tables + ["id"]]
                                 + ["Question to participant", "Participant Answer", "Coder", "Coding Questions",
                                    "Coding Answer", "\n"]))
            for individual in self.get_whole_table("individuals"):
                column = self.get_columns("individuals")
                individual = dict(zip(column, individual))
                for question in self.custom_tables:
                    for i in self.get_whole_table(question):
                        column = self.get_columns(question)
                        coding_questions = dict(zip(column, i))
                        if coding_questions["id"] == individual["id"]-1:
                            for coding_question in coding_questions:
                                if coding_question != "id" and coding_question != "coder":
                                    file.write("\t".join([str(individual[i]) for i in self.get_columns("individuals") if
                                                          i not in self.custom_tables + ["id"]]
                                                         + [str(self.__reverse_transform_column(question)),
                                                            str(individual[question]), coding_questions["coder"],
                                                            self.__reverse_transform_column(coding_question),
                                                            coding_questions[coding_question], "\n"]))

        titles = list()
        for i in ["individuals"] + self.custom_tables:
            for j in self.get_columns(i):
                titles.append((i, j))
        """
        columns = [i[1] for i in titles if i[0] == "individuals" and i[1] not
         in [self.__transform_column(i[0]) for i in self.custom_tables]]
        print(len(columns),columns)
        """
        '''
        command = """SELECT {} FROM individuals\n""".format(", ".join(list(map(".".join, titles)))) + "".join(
            ["""INNER JOIN {} ON {}\n""".format(i, """{}.id = individuals.id""".format(i)) for i in self.custom_tables])
        '''
        """
        print(command)
        c = self.conn.cursor()
        c.execute(command)
        res = c.fetchall()
        print(res)
        for i in res:
            print(i)
        print( titles )
        print([(i[0],self.__reverse_transform_column(i[1])) for i in titles])

        #with open(os.path.join(self.path,filename)):
        #    pass
        """


class CodingUnit(object):
    def __init__(self, project, question, answer, coding_questions, id_):
        self.question = question
        self.answer = answer
        self.coding_questions = coding_questions
        self.coding_answers = dict()
        self.id = id_
        self.project = project
        self["coder"] = project.coder

    def isFinished(self):
        res = True
        res &= all(i in self.coding_answers.keys() for i in self.coding_questions)
        res &= all(self.coding_answers[i] is not None for i in self.coding_answers)
        return res

    def __setitem__(self, key, value):
        self.coding_answers[key] = value
        self.project.store_answer(self.question, key, value, self.id)

    def __repr__(self):
        return "\n".join(["Coding unit: {} -> {}".format(self.question, self.answer)] + [
            "-{}\n\t-> {}".format(i, self.coding_answers.get(i, None)) for i in self.coding_questions])
