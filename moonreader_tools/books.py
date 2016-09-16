"""
Module, containing classes used to parse book data from files and string
"""


import os
import json

from moonreader_tools.conf import STAT_EXTENSION, NOTE_EXTENSION
from moonreader_tools.stat import Statistics
from moonreader_tools.parsers import MoonReaderNotes


class BookTypeError(ValueError):
    pass


class ParamTypeError(ValueError):
    pass


class NoteRepresentation(object):
    """This class wraps note objects and
    provides interface to update every note"""

    def __init__(self, notes):
        self._notes = notes

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._notes)

    def to_json(self):
        """Dumps object to json"""
        pass

    def remove(self, note_number):
        """Removes note from notes list"""


class Book(object):
    """One of the most important classes in hierarchy
    Represents generic book object, and hides all of the complexity
    of parsing, updating and writing to moonreader book files"""

    ALLOWED_TYPES = ("epub", "fb2", "pdf", "txt", "zip", "mobi")

    def __init__(self, title, stats, notes=None, book_type=""):
        """
        :param title: Book title
        :type title: str
        :param stats: Statistics object
        :type stats: moonreader_tools.stat.Statistics
        :param notes: list of Note objects
        :type notes: Iterable[Note]
        """
        self.title = title
        self.stats = stats
        self.type = book_type
        if notes is None:
            self.notes = []
        else:
            self.notes = notes

    @property
    def pages(self):
        return self.stats.pages

    @pages.setter
    def pages(self, value):
        self.stats.pages = value

    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, notes_iterable):
        if isinstance(notes_iterable, NoteRepresentation):
            self.__notes = notes_iterable
        else:
            self.__notes = NoteRepresentation(notes_iterable)

    @property
    def stats(self):
        return self.__stats

    @stats.setter
    def stats(self, stats_obj):
        if isinstance(stats_obj, dict):
            self.__stats = Statistics.from_dict(stats_obj)
        else:
            self.__stats = stats_obj

    @property
    def percentage(self):
        return self.stats.percentage

    @percentage.setter
    def percentage(self, value):
        self.stats.percentage = value

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
        """Takes tuple of statistics file path,
        and notes file path and creates Book object
        from them"""
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
        """Takes a dictionary with note and statistics files
        paths and file descriptors and builds Book object from them
        General dict structure is as follows:
        dict = {
            "stat_file": ("/my/filename.po", <file_descriptor_1>),
            "note_file": ("/my/filename.an", <file_descriptor_2>)
        }
        """
        fname = dct["stat_file"][0] if dct["stat_file"] else dct["note_file"][0]
        book_ext = cls._get_book_type(fname)
        book_title = cls._title_from_fname(fname)
        book_stat = Statistics.from_file_obj(dct["stat_file"][1])
        book_notes = MoonReaderNotes.from_file_obj(dct["note_file"][1], book_ext)
        return cls(book_title,
                   book_stat,
                   book_notes)

    @classmethod
    def _get_book_type(cls, filename,
                       default_type="",
                       allowed_types=None,
                       extensions=(NOTE_EXTENSION, STAT_EXTENSION)):
        """Extracts book type (pdf, fb2) from extension.
        E.g. given filename my_book.fb2.zip fb2 will be returned"""
        if allowed_types is None:
            allowed_types = cls.ALLOWED_TYPES
        if default_type:
            return default_type
        if not filename.endswith(extensions):
            err_msg = "Only files that end with {} are supported"
            raise BookTypeError(err_msg.format(", ".join(extensions)))
        splitted_title = filename.split(".")

        # Out book file should have at least two extensions
        # if default type is not specified
        if len(splitted_title) < 3:
            msg = "Incorrect filename, at least two extensions required: {}"
            raise BookTypeError(msg.format(filename))
        book_type = splitted_title[-2]

        cls.validate_book_ext(book_type)

        is_zip_ext = book_type == "zip"
        if not is_zip_ext:
            # If not ends with .zip we check only if type is supported
            cls.validate_book_ext(book_type)
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

    def save(self, path="", notes_file=None, stats_file=None):
        """Dump book object into corresponding notes and stats file
        :param path: output filename, notes and stats files
        will be generated automatically from this name
        :param notes_file: path to the ouput notes file, cannot be used
        together with the 'path' parameter. Should not include notes file ext
        :param stats_file: path to the ouput stratistics file, cannot be used
        together with the 'path' parameter. Should not include stats file ext
        """
        if path and any((notes_file, stats_file)):
            msg = """path param cannot be used together\
             with notes_file or stats_file params"""
            raise ParamTypeError(msg)
        if path:
            notes_file = ".".join([path, NOTE_EXTENSION])
            stats_file = ".".join([path, STAT_EXTENSION])
        self.to_notes_file(notes_file)
        self.to_stat_file(stats_file)

    def to_notes_string(self):
        """Dump given book back to the readable string
        (no compression applied)"""

    def to_notes_file(self, filepath):
        """Dump given book to the string ready to be
        written in file"""

    def to_stat_string(self):
        """Dumps statistics data to string"""
        pass

    def to_stat_file(self, filepah):
        """Dumps statistics data to file"""
        pass

    @classmethod
    def validate_book_ext(cls, ext):
        allowed = cls.ALLOWED_TYPES
        if ext.lower() not in allowed:
            msg = "Filetype ({}) is not supported. Supported types are: {}"
            raise BookTypeError(msg.format(ext, ", ".join(allowed)))
