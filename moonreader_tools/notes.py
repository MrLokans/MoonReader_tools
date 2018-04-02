"""Collection of classes that present different book formats' notes"""

from moonreader_tools.utils import date_from_long_timestamp


class Note(object):
    """
    A simple DTO representing book note in the system
    """
    _REPR_TEXT_LENGTH = 100

    def __init__(self, text, timestamp):
        self._text = text
        self._timestamp = timestamp

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text

    @property
    def created(self):
        return date_from_long_timestamp(self._timestamp)

    def __repr__(self):
        return '<Note: {}>'.format(self.text[:self._REPR_TEXT_LENGTH])

    def __str__(self):
        return self.__repr__()
