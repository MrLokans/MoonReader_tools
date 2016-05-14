"""
Module, containing classes used to parse book data from files and string
"""


import os
import json

from .stat import Statistics
from .parsers import MoonReaderNotes


class Book(object):

    def __init__(self, title, stats, notes):
        self.title = title
        self._stats = stats
        self.pages = self._stats.pages
        self.percentage = self._stats.percentage
        self.notes = notes

    def to_dict(self):
        """Serialize book to dictionary"""
        try:
            d = {
                "title": self.title,
                "pages": self.pages,
                'percentage': self.percentage,
                'notes': [note.to_dict() for note in self.notes]
            }
        except:
            print(self.title)
            print(self.pages)
            print(self.percentage)
            print(self.notes)
            exit()
        return d

    def to_json(self):
        """Serializes book class into json"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def _from_file_tuple(cls, tpl):
        stat_file, note_file = tpl
        fname = stat_file if stat_file else note_file
        title = cls._title_from_fname(fname)
        return cls(title,
                   Statistics.from_file(note_file),
                   MoonReaderNotes.from_file(stat_file))

    @classmethod
    def _from_fobj_dict(cls, dct):
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
        return cls("", None, None)

