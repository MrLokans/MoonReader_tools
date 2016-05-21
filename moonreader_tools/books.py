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

    def __init__(self, notes):
        self._notes = notes

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._books)


class Book(object):

    ALLOWED_TYPES = ("epub", "fb2", "pdf", "txt", "zip", "mobi")

    def __init__(self, title, stats, notes=None, book_type=""):
        self.title = title
        self._stats = stats
        self.pages = self._stats.pages
        self.percentage = self._stats.percentage
        self.type = book_type
        if notes is None:
            self.notes = []
        else:
            self.notes = notes
        # self._notes = NoteRepresentation(notes)

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
        book_type = cls._get_book_type(fname)
        return cls(title,
                   Statistics.from_file(note_file),
                   MoonReaderNotes.from_file(stat_file),
                   book_type=book_type)

    @classmethod
    def from_fobj_dict(cls, dct):
        fname = dct["stat_file"][0] if dct["stat_file"] else dct["note_file"][0]
        book_ext = cls._get_book_type(fname)
        book_title = cls._title_from_fname(fname)
        book_stat = Statistics.from_file_obj(dct["stat_file"][1])
        book_notes = MoonReaderNotes.from_file_obj(dct["note_file"][1], book_ext)
        return cls(book_title,
                   book_stat,
                   book_notes)

    @classmethod
    def _get_book_type(cls, filename, default_type="", allowed_types=None):
        """Extracts book type (pdf, fb2) from extension.
        E.g. given filename my_book.fb2.zip fb2 will be returned"""
        if allowed_types is None:
            allowed_types = cls.ALLOWED_TYPES
        if default_type:
            return default_type
        splitted_title = filename.split(".")

        # Out book file should have at lest to extensions
        # if default type is not specified
        if len(splitted_title) < 3:
            msg = "Incorrect filename, at least two extensions required: {}"
            raise ValueError(msg.format(filename))
        book_type = splitted_title[-2]

        is_zip_ext = book_type == "zip"
        if not is_zip_ext:
            # If not ends with .zip we check only if type is supported
            if book_type not in cls.ALLOWED_TYPES:
                msg = "Filetype is not supported. Supported types are: {}"
                raise ValueError(msg.format(", ".join(cls.ALLOWED_TYPES)))
        # if it ends with zip we should check whether it has extra extension
        # just before .zip
        elif is_zip_ext and len(splitted_title) > 2:
            # if preceding extension is allowed we return it
            allowed_ext = splitted_title[-3].lower() in cls.ALLOWED_TYPES
            if allowed_ext:
                book_type = splitted_title[-3]
            else:
                book_type = "zip"
        # otherwise it is .zip file
        else:
            book_type = "zip"
        return book_type

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

    def to_notes_string(self):
        """Dump given book back to the readable string
        (no compression applied)"""

    def to_notes_file(self, filepath):
        """Dump given book to the string ready to be
        written in file"""

    def to_stat_string(self):
        pass

    def to_stat_file(self, filepah):
        pass
