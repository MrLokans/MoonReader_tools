import logging

from moonreader_tools.books import Book
from moonreader_tools.parsers import PDFNoteParser, FB2NoteParser, StatsAccessor
from moonreader_tools.utils import title_from_fname, get_book_type

logger = logging.getLogger()


class BookParser:
    """
    This class wraps underlying type-specific file parsers
    and attempts to read book notes and statistics
    """

    def __init__(self, book_type: str, **kwargs) -> None:
        self._book_name = kwargs.get("book_name", "")
        self._notes_fobj = None
        self._stats_fobj = None
        self._book_type = book_type
        self._stats_reader = kwargs.get("stats_reader", StatsAccessor())

    @classmethod
    def from_files(cls, notes_file, stats_file):
        """
        Attempt to build the Book object
        using two files with statistics and notes.
        """
        book_title = title_from_fname(notes_file or stats_file)
        book_type = get_book_type(notes_file or stats_file)
        notes_fobj, stats_fobj = open(notes_file, "rb"), open(stats_file, "rb")
        return cls.from_file_obj_tuple(book_type, book_title, notes_fobj, stats_fobj)

    @classmethod
    def from_file_obj_tuple(cls, book_type, book_title, notes_fobj, stats_fobj):
        instance = cls(book_type)
        instance.set_book_name(book_title)
        instance.set_notes_fobj(notes_fobj)
        instance.set_stats_fobj(stats_fobj)
        return instance

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *args):
        if self._notes_fobj:
            self._notes_fobj.close()
        if self._stats_fobj:
            self._stats_fobj.close()
        if exc_type:
            return False

    def set_book_name(self, book_name: str):
        self._book_name = book_name
        return self

    def set_notes_file(self, note_filepath: str):
        if note_filepath:
            self.set_notes_fobj(open(note_filepath, "rb"))
        return self

    def set_stats_file(self, stats_filepath: str):
        if stats_filepath:
            self.set_stats_fobj(open(stats_filepath, "rb"))
        return self

    def set_notes_fobj(self, note_fobj):
        self._notes_fobj = note_fobj
        return self

    def set_stats_fobj(self, stats_fileobj):
        self._stats_fobj = stats_fileobj
        return self

    def get_note_reader_by_type(self, book_type):
        book_type = book_type.lower()
        if book_type in ["pdf"]:
            return PDFNoteParser()
        elif book_type in ["fb2", "epub"]:
            return FB2NoteParser()
        else:
            raise ValueError("Unknown book type: %s", book_type)

    def build(self) -> "Book":
        """Constructs actual book instance
        """
        if not all([self._stats_fobj, self._notes_fobj]):
            logger.error(
                "Both stats file and notes file are not set for book %s.",
                self._book_name,
            )
            return Book(title=self._book_name)
        note_reader = self.get_note_reader_by_type(self._book_type)
        notes, stats = [], None  # type: ignore
        if self._notes_fobj:
            notes = note_reader.from_file_obj(self._notes_fobj)
        if self._stats_fobj:
            stats = self._stats_reader.stats_from_file_obj(self._stats_fobj)
        return Book(title=self._book_name, stats=stats, notes=notes)
