import logging
import os
import random
import sqlite3
from builtins import str
import yaml
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    criterias = relationship("Criteria", back_populates='question', lazy=True)
    answers = relationship("Answer", back_populates='question', lazy=True)

class Criteria(Base):
    __tablename__ = "criteria"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    question_id = Column(Integer, ForeignKey('question.id'), nullable=False)
    question = relationship("Question",back_populates="criterias")
    codings = relationship("Coding", back_populates="criteria")

class Answer(Base):
    __tablename__ = "answer"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    question_id = Column(Integer, ForeignKey('question.id'), nullable=False)
    question = relationship("Question",back_populates="answers")
    codings = relationship("Coding", back_populates="answer")
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User",back_populates="answers")

class Coding(Base):
    __tablename__ = "coding"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    notes = Column(String)
    answer_id = Column(Integer, ForeignKey('answer.id'), nullable=False)
    answer = relationship("Answer",back_populates="codings")
    criteria_id = Column(Integer, ForeignKey('criteria.id'), nullable=False)
    criteria = relationship("Criteria",back_populates="codings")
    coder = Column(String)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    facts = Column(PickleType)
    answers = relationship("Answer", back_populates="user",lazy=True)

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
        if coder is not None:
            self.coder = coder
        else:
            raise Exception("Please define the coder!")
        # if file not exists
        self.separator = kwargs["separator"]
        self.eng = create_engine('sqlite:///{}'.format(file),echo=True)
        Base.metadata.bind = self.eng
        Base.metadata.create_all()
        self.Session = sessionmaker(bind=self.eng)
        # self.conn = sqlite3.connect(os.path.join(path, file))
        self.init_db(path, *args, **kwargs)
        self.load_config(path, kwargs["config"])
        self.current_coding_unit = None

    def load_config(self, path, configfile):
        with open(os.path.join(path, configfile)) as file:
            questions = yaml.load(file)
        if questions is None:
            raise Exception("Could not read the Config file!")
        session = self.Session()
        with session.no_autoflush:
            for question in questions["questions"]:
                q = Project.get_question(session, question["text"])
                for criteria in question["coding"]:
                    Project.get_criteria(session, criteria["criteria"], q)
            session.commit()

    def load_data(self,path,datafile, separator):
        with open(os.path.join(path, datafile)) as file:
            data = Project.handleCSV(file, separator)
        if len(data) > 1:
            titles = set(data[0].keys())
            session = self.Session()
            with session.no_autoflush:
                questions = set([i.text for i in session.query(Question)])
                user_data = titles - questions
                for user in data:
                    # TODO: get_user muss noch alle antworten Checken.
                    user_dict = {key:user[key] for key in user_data}
                    u = Project.get_user(session,user_dict)
                    for question in questions:
                        q = Project.get_question(session,question)
                        Project.get_answer(session,text=user[question],question=q,user=u)
                session.commit()
        else:
            raise Exception("Check your separator!")

    @staticmethod
    def get_user(session,facts,answers=None):
        # TODO: write test to check if the dictionary check works correctly here
        u_all = session.query(User).filter_by(facts=facts).all()
        if len(u_all) > 1:
            raise Exception("Found duplicate user with ids {}"
                            .format(", ".join([c.id for c in u_all])))
        elif len(u_all) == 1:
            # Na bravo. Passt doch. Evtl success loggen
            c = u_all[0]
        else:
            c = User(facts=facts)
            session.add(c)
        return c

    @staticmethod
    def get_question(session, text):
        q_all = session.query(Question).filter_by(text=text).all()
        if len(q_all) > 1:
            raise Exception("Found duplicate question for \"{}\" with ids {}".format(text,
                                                                                     ", ".join([q.id for q in q_all])))
        elif len(q_all) == 1:
            q = q_all[0]
        else:
            q = Question(text=text)
            session.add(q)
        return q

    @staticmethod
    def get_criteria(session, text, question):
        c_all = session.query(Criteria).filter_by(text=text, question=question).all()
        if len(c_all) > 1:
            raise Exception("Found duplicate criteria for criteria \"{}\" of the question \"{}\" with ids {}"
                            .format(text, question.text, ", ".join([c.id for c in c_all])))
        elif len(c_all) == 1:
            # Na bravo. Passt doch. Evtl success loggen
            c = c_all[0]
        else:
            c = Criteria(question=question, text=text)
            session.add(c)
        return c

    @staticmethod
    def get_answer(session, text, question, user):
        a_all = session.query(Answer).filter_by(text=text, question=question,user=user).all()
        if len(a_all) > 1:
            raise Exception("Found duplicate answer for answer \"{}\" of the question \"{}\" of the user {} with ids {}"
                            .format(text, question.text, user.id, ", ".join([a.id for a in a_all])))
        elif len(a_all) == 1:
            # Na bravo. Passt doch. Evtl success loggen
            a = a_all[0]
        else:
            a = Answer(question=question, text=text, user=user)
            session.add(a)
        return a

    def init_db(self, path, *args, **kwargs):
        if "config" in kwargs and kwargs["config"] is not None:
            self.load_config(path,kwargs["config"])
        if "data" in kwargs and kwargs["data"] is not None:
            self.load_data(path,kwargs["data"],kwargs["separator"])

        # c = self.conn.cursor()
        # c.execute("""CREATE TABLE IF NOT EXISTS vars (key text, value text)""")
        # c.execute("""CREATE TABLE IF NOT EXISTS translation (clear text, translated text, UNIQUE(clear, translated))""")
        # self.conn.commit()



        # if "data" in kwargs:
        #     if kwargs["data"] is None:
        #         raise Exception("Please provide a data file.")
        #
        #     with open(os.path.join(path, kwargs["data"])) as file:
        #         res = Project.handleCSV(file, kwargs["separator"])
        #
        #     if len(res):
        #         titles = list(res[0].keys())
        #         cquery = ["{} {}".format(self.__transform_column(i), "TEXT") for i in titles]
        #         cquery = ", ".join(cquery)
        #         c.execute("""CREATE TABLE IF NOT EXISTS individuals (id INTEGER PRIMARY KEY,{})""".format(cquery))
        #         self.conn.commit()
        #         for row in res:
        #             columns = []
        #             values = []
        #             for column in row:
        #                 if len(row[column].strip()) != 0:
        #                     columns.append(self.__transform_column(column))
        #                     values.append((row[column]))
        #             aquery = " AND ".join(i + "=?" for i in columns)
        #
        #             if len(values):
        #                 c.execute("""SELECT id FROM individuals WHERE {}""".format(aquery), values)
        #                 identifier = c.fetchone()
        #                 if not identifier:
        #                     c.execute("""INSERT INTO individuals ({}) VALUES ({})""".format(", ".join(columns),
        #                                                                                     " ,".join(
        #                                                                                         "?" for _ in values)),
        #                               values)
        #                     self.conn.commit()
        # if "config" in kwargs:
        #     c.execute("""CREATE TABLE IF NOT EXISTS question_assoc (question text, coding text)""")
        #     with open(os.path.join(path, kwargs["config"])) as file:
        #         questions = yaml.load(file)
        #         if questions is None:
        #             raise Exception("Could not read the Config file!")
        #     for question in questions["questions"]:
        #         qquery = ", ".join(
        #             [self.__transform_column(i["criteria"]) + " TEXT" for i in question["coding"]] + ["coder TEXT"])
        #         c.execute("""CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, {})""".format(
        #             self.__transform_column(question["text"]), qquery))
        #         for i in question["coding"]:
        #             c.execute("""INSERT INTO question_assoc SELECT ?,?
        #                           WHERE NOT EXISTS(SELECT 1 FROM question_assoc WHERE question=? AND coding=?)""",
        #                       (question["text"], i["criteria"], question["text"], i["criteria"]))
        #         self.conn.commit()

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
                if len(titles) == 1:
                    logging.log(logging.CRITICAL, "The data file contains only one column with this separator. "
                                                  "Check your separator.")
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
        session = self.Session()
        for question in session.query(Question):
            criterias = list(session.query(Criteria).filter_by(question=question))
            # TODO: Adapt for other databases
            for answer in session.query(Answer).filter_by(question=question).order_by(func.random()):
                amount_of_codings_relevant = session.query(Coding).filter_by(answer=answer, coder=self.coder).count()
                if amount_of_codings_relevant > len(criterias):
                    raise Exception("Too many codings found, more than one for each coding necessary.\n {}"
                                    .format("\n".join(session.query(Coding).filter_by(answer=answer, coder=self.coder))))
                elif amount_of_codings_relevant < len(criterias):
                    coding_done = []
                    for coding in session.query(Coding).filter_by(answer=answer, coder=self.coder):
                        if coding.text:
                            coding_done.append(coding.criteria)
                    self.current_coding_unit = CodingUnit(self, question, answer, criterias, coding_done, session)
                    return self.current_coding_unit

        raise StopIteration

        # for table in self.custom_tables:
        #     c = self.conn.cursor()
        #     c.execute("""SELECT * FROM {}""".format(table))
        #
        #     ids_in_table = c.fetchall()
        #     ids_in_table[:] = [i for i in ids_in_table if None not in i]
        #     if amount_of_individuals > len(ids_in_table):
        #         entries = set(range(amount_of_individuals)) - set([i[0] for i in ids_in_table])
        #         entry = random.choice(list(entries))
        #         c.execute("""SELECT {} FROM individuals""".format(table))
        #         coding_answer = c.fetchall()[entry][0]
        #         coding_question = self.__reverse_transform_column(table)
        #         questions = self.get_questions(coding_question)
        #         questions[:] = [i for i in questions if not self.__question_already_answered(coding_question, i, entry)]
        #         if len(questions) == 0:
        #             c.execute("""SELECT * FROM question_assoc""")
        #             res = c.fetchall()
        #             for i in res:
        #                 print(i, len(i[0]), len(coding_question), repr(coding_question))
        #             raise Exception("This should not happen")
        #         self.current_coding_unit = CodingUnit(self, coding_question, coding_answer, questions, entry)
        #         return self.current_coding_unit


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

    def export2(self, filename="out.txt"):
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

    def export(self,filename="out.csv"):
        with open(os.path.join(self.path, filename), "w") as file:
            session = self.Session()
            # TODO: Make user safe again
            random_user = session.query(User).first()
            file.write(self.separator.join(list(random_user.facts.keys())+["Question to Participant","Participant answer",
                                                           "Coding Criteria","Coding Value","Coder"])+"\n")

            for coding in session.query(Coding).filter_by(coder=self.coder):
                answer = coding.answer
                user = answer.user
                criteria = coding.criteria
                question = criteria.question
                file.write(self.separator.join([user.facts[key] for key in user.facts]+[question.text,answer.text,
                                     criteria.text,coding.text,self.coder])+"\n")


class CodingUnit(object):
    def __init__(self, project, question, answer, criterias, coding_done, session):
        self.question = question
        self.answer = answer
        self.session = session
        self.criterias = criterias
        self.criteria_str2obj = {i.text:i for i in criterias}
        self.coding_done = coding_done
        self.coding_answers = {i.text:i for i in coding_done}
        self.project = project

    def isFinished(self):
        res = True
        res &= all(i.text in self.coding_answers.keys() for i in self.criterias)
        res &= all(self.coding_answers[i] is not None for i in self.coding_answers)
        return res

    def __setitem__(self, criteria, value):
        self.coding_answers[criteria.text] = Coding(text=value,answer=self.answer, criteria=criteria,coder=self.project.coder)
        self.session.add(self.coding_answers[criteria.text])
        self.session.commit()

    def __repr__(self):
        return "\n".join(["Coding unit: {} -> {}".format(self.question.text, self.answer.text)] + [
            "-{}\n\t-> {}".format(i, self.coding_answers.get(i, None)) for i in self.criteria_str2obj.keys()])
