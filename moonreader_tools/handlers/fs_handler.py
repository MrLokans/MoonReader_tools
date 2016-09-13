import logging

from moonreader_tools.books import Book
from moonreader_tools.utils import (
    get_moonreader_files,
    get_same_book_files
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
            for book_files_tuple in tuples:
                b = Book.from_file_tuple(book_files_tuple)
                yield b
        except Exception:
            err_msg = "Exception occured when creating book object."
            logging.exception(err_msg)
