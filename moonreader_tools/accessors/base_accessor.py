import abc


class BaseNoteAccessor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def notes_to_file(self, notes, filename):
        pass

    @abc.abstractmethod
    def notes_from_file(self, filename, **kwargs):
        pass

    @abc.abstractmethod
    def notes_from_string(self, text, **kwargs):
        pass

    @abc.abstractmethod
    def notes_to_string(self, notes):
        pass
