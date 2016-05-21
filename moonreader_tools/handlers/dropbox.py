import logging

import dropbox

from .drobpox_utils import (
    filepaths_from_metadata,
    dicts_from_pairs,
)
from moonreader_tools.books import Book
from moonreader_tools.utils import (
    get_moonreader_files_from_filelist,
    get_same_book_files
)


class DropboxDownloader(object):
    """Class to obtain bookdata from dropbox syncronized account"""
    DEFAULT_DROPBOX_PATH = 'Books/.Moon+/Cache'

    def __init__(self, access_token,
                 books_path="",
                 workers=8):
        if not access_token:
            raise ValueError("Access token must be specified.")
        if not books_path:
            books_path = DropboxDownloader.DEFAULT_DROPBOX_PATH
        self.access_token = access_token
        self.books_path = books_path
        self.workers = workers

    def get_books(self, path="", book_count=None):
        """Obtains book objects from dropbox folder"""
        if not path and not self.books_path:
            raise ValueError("Path to read data from is not specified")
        if not path:
            path = self.books_path

        client = dropbox.client.DropboxClient(self.access_token)
        meta = client.metadata(path)
        files = filepaths_from_metadata(meta)
        moonreader_files = get_moonreader_files_from_filelist(files)
        if book_count is not None:
            file_pairs = get_same_book_files(moonreader_files)[:book_count]
        else:
            file_pairs = get_same_book_files(moonreader_files)
        dicts = dicts_from_pairs(client, file_pairs, workers=self.workers)
        books_data = []
        for book_dict in dicts:
            try:
                book = Book.from_fobj_dict(book_dict)
                books_data.append(book)
            except Exception:
                err_msg = "Exception occured when creating book object."
                logging.exception(err_msg)

        return books_data
