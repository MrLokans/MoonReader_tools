import logging
import pathlib
from typing import Optional

from moonreader_tools.parsers.base import BookParser
from moonreader_tools.utils import (
    get_moonreader_files,
    get_same_book_files,
    title_from_fname,
    get_book_type,
)


class FilesystemFinder:
    """Class to obtain books from file system
    Usage example:

    extractor = FilesystemDownloader('/some/path/')
    for book in extractor.get_books():
        print(book.title)
    """

    def __init__(self, path=""):
        self.path = pathlib.Path(path)

    def get_books(self, book_count: Optional[int] = None):
        """Obtains book objects from local directory"""
        if not self.path.exists() or not self.path.is_dir():
            raise ValueError("Path does not exist or is not a dir.")

        moonreader_files = get_moonreader_files(self.path)
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
