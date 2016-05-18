import abc


class BaseParser(object):
    """Base class for every parser"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def from_text(self, text):
        """Parse given string and return a sequence of note objects"""
        pass

    @abc.abstractmethod
    def dump_to_string(self, book):
        """Dump given book back to the readable string
        (no compression applied)"""

    @abc.abstractmethod
    def dump_to_file_content(self, book):
        """Dump given book to the string ready to be
        written in file"""
