from abc import abstractmethod


class Command(object):
    @abstractmethod
    def do(self):
        pass


class UndoableCommand(object):
    @abstractmethod
    def undo(self):
        pass


class CommandManager(object):
    def __init__(self, stack):
        self.stack = stack

    def execute(self, command):
        self.stack.push(command)
        command.do()

    def undo(self):
        if self.stack.count > 0:
            self.stack.pop().undo()
