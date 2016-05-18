"""
Module, containing classes used to parse book data from files and string
"""


import os
import json

from .stat import Statistics
from .parsers import MoonReaderNotes


class NoteRepresentation(object):
    """This class wraps note objects and
    provides interface to update every note"""
    pass


class Book(object):

    def __init__(self, title, stats, notes):
        self.title = title
        self._stats = stats
        self.pages = self._stats.pages
        self.percentage = self._stats.percentage
        self.notes = notes
        self._notes = NoteRepresentation(notes)

    def to_dict(self):
        """Serialize book to dictionary"""
        book_dict = {
            "title": self.title,
            "pages": self.pages,
            'percentage': self.percentage,
            'notes': [note.to_dict() for note in self.notes]
        }
        return book_dict

    def to_json(self):
        """Serializes book class into json"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_file_tuple(cls, tpl):
        stat_file, note_file = tpl
        fname = stat_file if stat_file else note_file
        title = cls._title_from_fname(fname)
        return cls(title,
                   Statistics.from_file(note_file),
                   MoonReaderNotes.from_file(stat_file))

    @classmethod
    def from_fobj_dict(cls, dct):
        fname = dct["stat_file"][0] if dct["stat_file"] else dct["note_file"][0]
        book_ext = fname.split('.')[-2]
        if book_ext == "zip":
            book_ext = fname.split('.')[-3]
        book_title = cls._title_from_fname(fname)
        book_stat = Statistics.from_file_obj(dct["stat_file"][1])
        book_notes = MoonReaderNotes.from_file_obj(dct["note_file"][1], book_ext)
        return cls(book_title,
                   book_stat,
                   book_notes)

    def read_stat(self, text="", filename=""):
        """Update reading statistics representation
        from string of from specified file"""
        stat = None
        if text:
            stat = Statistics.from_string(stat)
        elif filename:
            stat = Statistics.from_file(filename)
        self._stats = stat
        return stat

    @classmethod
    def _title_from_fname(cls, fname):
        """Extracts book title from file name"""
        fname = os.path.split(fname)[-1]
        if fname.endswith((".po", ".an")):
            fname = fname[:-3]
        if fname.endswith(".fb2.zip"):
            fname = fname[:-8]
        if fname.endswith((".fb2", ".pdf")):
            fname = fname[:-4]
        if fname.endswith(".epub"):
            fname = fname[:-5]
        return fname

    def __str__(self):
        return "<Book> {}: {} notes".format(self.title, len(self.notes))

    def __repr__(self):
        return str(self)

    @classmethod
    def empty_book(cls):
        """Construct empty book object"""
        return cls("", None, None)
