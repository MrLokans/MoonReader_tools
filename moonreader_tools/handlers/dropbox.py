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
                 books_path=""):
        if not access_token:
            raise ValueError("Access token must be specified.")
        if not books_path:
            books_path = DropboxDownloader.DEFAULT_DROPBOX_PATH
        self.access_token = access_token
        self.books_path = books_path

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
        dicts = dicts_from_pairs(client, file_pairs)
        books_data = [Book.from_fobj_dict(d).to_dict()
                      for d in dicts]
        return books_data
