import logging
import os

import yaml
from sqlalchemy import Column, create_engine, DateTime, ForeignKey, func, Integer, PickleType, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from .utils import lcs, match_lists

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
    question = relationship("Question", back_populates="criterias")
    codings = relationship("Coding", back_populates="criteria")


class Answer(Base):
    __tablename__ = "answer"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    question_id = Column(Integer, ForeignKey('question.id'), nullable=False)
    question = relationship("Question", back_populates="answers")
    codings = relationship("Coding", back_populates="answer")
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship("User", back_populates="answers")


class Coding(Base):
    __tablename__ = "coding"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    notes = Column(String)
    answer_id = Column(Integer, ForeignKey('answer.id'), nullable=False)
    answer = relationship("Answer", back_populates="codings")
    criteria_id = Column(Integer, ForeignKey('criteria.id'), nullable=False)
    criteria = relationship("Criteria", back_populates="codings")
    coder = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    facts = Column(PickleType)
    answers = relationship("Answer", back_populates="user", lazy=True)


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
        self.logger = logging.getLogger(__name__)
        self.path = path
        self.file = file
        if coder is not None:
            self.coder = coder
        else:
            raise Exception("Please define the coder!")
        # if file not exists
        self.separator = kwargs["separator"]
        self.eng = create_engine('sqlite:///{}'.format(file))
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

    def load_data(self, path, datafile, separator):
        with open(os.path.join(path, datafile)) as file:
            data = Project.handle_csv(file, separator)
        if len(data) > 1:
            titles = set(data[0].keys())
            session = self.Session()
            with session.no_autoflush:
                # Match all
                questions = set([i.text for i in session.query(Question)])
                translation = match_lists(titles, questions)
                user_data = titles - set(translation.values())
                for user in data:
                    # TODO: get_user muss noch alle antworten Checken.
                    user_dict = {key: user[key] for key in user_data}
                    u = Project.get_user(session, user_dict)
                    for question in questions:
                        q = Project.get_question(session, question)
                        Project.get_answer(session, user[translation[question]], question=q, user=u)
                session.commit()
        else:
            raise Exception("Check your separator!")

    def match(self, list_, candidate):
        if candidate in list_:
            return candidate
        else:
            self.logger.info("Didn't match at first try. Attempting smart match.")
            candidate = candidate.strip().lstrip()
            best = 0
            second = 0
            best_match = None
            sum_score = 0
            for entry in list_:
                score = 1.0 * len(lcs(entry, candidate)) / len(candidate) * min(len(entry), len(candidate)) / max(
                    len(entry), len(candidate))
                sum_score += score
                if score > second:
                    if score > best:
                        second, best = best, score
                        best_match = entry
                    else:
                        second = score
            if best > 3 * second:
                self.logger.info(
                    "Could match {} onto {} from {} with probability {}.".format(candidate, best_match, list_,
                                                                                 second / best))
                return best_match
            else:
                raise Exception(
                    "Couldn't match {} onto {}. Best guess: {}, with probability {}. Error probability at {}.".format(
                        candidate, list_, best_match, best, second / best))

    @staticmethod
    def get_user(session, facts):
        # TODO: write test to check if the dictionary check works correctly here, but apparently it does
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
    def get_coding(session, answer, criteria, coder, text, notes):
        c_all = session.query(Coding).filter_by(answer=answer, criteria=criteria, coder=coder).all()
        if len(c_all) > 1:
            raise Exception("Found duplicate coding for criteria \"{}\" of the answer \"{}\" with ids {}"
                            .format(criteria.text, answer.text, ", ".join([c.id for c in c_all])))
        elif len(c_all) == 1:
            # Na bravo. Passt doch. Evtl success loggen
            c = c_all[0]
        else:
            c = Coding(answer=answer, criteria=criteria, text=text, notes=notes, coder=coder)
            session.add(c)
        return c

    @staticmethod
    def get_answer(session, text, question, user):
        a_all = session.query(Answer).filter_by(text=text, question=question, user=user).all()
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
            self.load_config(path, kwargs["config"])
        if "data" in kwargs and kwargs["data"] is not None:
            self.load_data(path, kwargs["data"], kwargs["separator"])

    @staticmethod
    def handle_csv(file, separator):
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

    def __iter__(self):
        return self

    def coding_is_finished(self, coding):
        session = self.Session()
        done = len(coding.answer.codings)
        todo = session.query(Criteria).filter_by(question=coding.answer.question).count()
        return done == todo

    def next_new(self):
        if self.current_coding_unit is not None:
            if not self.current_coding_unit.is_finished():
                return self.current_coding_unit
        session = self.Session()
        for question in session.query(Question):
            criterias = question.criterias
            # TODO: Adapt for other databases
            for answer in session.query(Answer).filter_by(question=question).order_by(func.random()):
                amount_of_codings_relevant = session.query(Coding).filter_by(answer=answer, coder=self.coder).count()
                if amount_of_codings_relevant > len(criterias):
                    raise Exception(
                        "Too many codings found, more than one for each coding necessary.\n {}"
                        .format("\n".join(session.query(Coding).filter_by(answer=answer, coder=self.coder))))
                elif amount_of_codings_relevant < len(criterias):
                    return self.build_current_coding_unit(answer, session)
        raise StopIteration

    def previous(self):
        session = self.Session()
        answer = self.current_coding_unit.answer
        if len(answer.codings):
            for coding in session.query(Coding) \
                    .filter(Coding.time_created < answer.codings[0].time_created) \
                    .order_by(Coding.time_created.desc()):
                if not coding.answer.id == answer.id:
                    return self.build_current_coding_unit(coding.answer, session)
        else:
            for coding in session.query(Coding).order_by(Coding.time_created.desc()):
                if not coding.answer.id == answer.id:
                    return self.build_current_coding_unit(coding.answer, session)
        return self.current_coding_unit

    def next(self):
        session = self.Session()
        answer = self.current_coding_unit.answer
        if len(answer.codings):
            for coding in session.query(Coding) \
                    .filter(Coding.time_created > answer.codings[0].time_created) \
                    .order_by(Coding.time_created):
                if not coding.answer.id == answer.id:
                    return self.build_current_coding_unit(coding.answer, session)
        return self.next_new()

    def resume(self):
        session = self.Session()
        last_updated = session.query(Coding).filter(Coding.time_updated.isnot(None)).order_by(
            Coding.time_updated.desc()).first()
        last_created = session.query(Coding).order_by(Coding.time_updated.desc()).first()
        if last_created:
            if last_updated:
                if last_updated.time_updated > last_created.time_created:
                    if not self.coding_is_finished(last_updated):
                        return self.build_current_coding_unit(last_updated.answer, session)
            if not self.coding_is_finished(last_created):
                return self.build_current_coding_unit(last_created.answer, session)
        return self.next_new()

    def build_current_coding_unit(self, answer, session):
        coding_done = {}
        for coding in session.query(Coding).filter_by(answer=answer, coder=self.coder):
            if coding.text:
                coding_done[coding.criteria] = coding
        self.current_coding_unit = CodingUnit(self, answer.question, answer, answer.question.criterias, coding_done,
                                              session)
        return self.current_coding_unit

    def export(self, filename="out.csv"):
        with open(os.path.join(self.path, filename), "w") as file:
            session = self.Session()
            # TODO: Make user safe again
            random_user = session.query(User).first()
            file.write(
                self.separator.join(list(random_user.facts.keys()) + ["Question to Participant", "Participant answer",
                                                                      "Coding Criteria", "Coding Value",
                                                                      "Coder", "Notes"]) + "\n")

            for coding in session.query(Coding).filter_by(coder=self.coder):
                answer = coding.answer
                user = answer.user
                criteria = coding.criteria
                question = criteria.question
                file.write(self.separator.join([user.facts[key] for key in user.facts] + [question.text, answer.text,
                                                                                          criteria.text, coding.text,
                                                                                          self.coder,
                                                                                          coding.notes]) + "\n")


class CodingUnit(object):
    def __init__(self, project, question, answer, criterias, coding_done, session):
        self.question = question
        self.answer = answer
        self.session = session
        self.criterias = criterias
        self.criteria_str2obj = {i.text: i for i in criterias}
        self.coding_done = coding_done
        self.coding_answers = {i.text: i for i in coding_done}
        self.project = project

    def is_finished(self):
        res = True
        res &= all(i.text in self.coding_answers.keys() for i in self.criterias)
        res &= all(self.coding_answers[i] is not None for i in self.coding_answers)
        return res

    def set_value(self, criteria, value, notes):
        self.coding_answers[criteria.text] = Project.get_coding(session=self.session, text=value, answer=self.answer,
                                                                criteria=criteria,
                                                                coder=self.project.coder, notes=notes)
        self.session.commit()

    def __repr__(self):
        return "\n".join(["Coding unit: {} -> {}".format(self.question.text, self.answer.text)] + [
            "-{}\n\t-> {}".format(i, self.coding_answers.get(i, None)) for i in self.criteria_str2obj.keys()])
