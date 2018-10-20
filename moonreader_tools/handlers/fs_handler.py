import logging

from moonreader_tools.parsers.base import BookParser
from moonreader_tools.utils import (
    get_moonreader_files,
    get_same_book_files,
    get_book_type,
    title_from_fname,
)


class FilesystemDownloader(object):
    """Class to obtain books from file system
    Usage example:

    handler = FilesystemDownloader()
    books = handler.get_books('/books/path/')
    """

    def __init__(self, books_path=""):
        self.books_path = books_path

    def get_books(self, path="", book_count=None):
        """Obtains book objects from local directory"""
        if not path and not self.books_path:
            raise ValueError("Path to read data from is not specified")
        if not path:
            path = self.books_path

        moonreader_files = get_moonreader_files(path)
        tuples = get_same_book_files(moonreader_files)
        try:
            for note_file, stat_file in tuples:
                book_name = title_from_fname(note_file or stat_file)
                book_type = get_book_type(note_file or stat_file)
                with BookParser(book_type=book_type) as reader:
                    reader = (
                        reader.set_notes_file(note_file)
                        .set_stats_file(stat_file)
                        .set_book_name(book_name)
                    )
                    yield reader.build()
        except Exception:
            err_msg = "Exception occured when creating book object."
            logging.exception(err_msg)
