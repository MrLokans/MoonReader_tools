import logging

from moonreader_tools.parsers.base import BookParser
from .drobpox_utils import extract_book_paths_from_dir_entries, dicts_from_pairs
from moonreader_tools.utils import (
    get_moonreader_files_from_filelist,
    get_same_book_files,
    title_from_fname,
    get_book_type,
)


class DropboxDownloader(object):
    """Class to obtain bookdata from dropbox syncronized account"""

    _DEFAULT_DROPBOX_PATH = "/Apps/Books/.Moon+/Cache"

    def __init__(self, dropbox_client, books_path="", workers=8, logger=None):
        """

        :param dropbox_client: Instantiated dropbox client
        :param books_path: Absolute path to dropbox's \
        dir with syncronized notes
        :param workers: number of concurrent workers to download\
        data from Dropbox
        """

        self.__dropbox_client = dropbox_client
        self.books_path = books_path or self._DEFAULT_DROPBOX_PATH
        self.workers = workers

    def get_books(self, path: str = "", book_count: int = None):
        """Obtains book objects from dropbox folder
        :param path: Dropbox directory with syncronized\
        book data
        :param book_count: number of books to read
        """
        if not path and not self.books_path:
            raise ValueError("Path to read data from is not specified")
        if not path:
            path = self.books_path

        folder_contents = self.__dropbox_client.files_list_folder(path)
        files = extract_book_paths_from_dir_entries(folder_contents.entries)
        moonreader_files = get_moonreader_files_from_filelist(files)
        if book_count is not None:
            file_pairs = get_same_book_files(moonreader_files)[:book_count]
        else:
            file_pairs = get_same_book_files(moonreader_files)

        for book_dict in dicts_from_pairs(
            self.__dropbox_client, file_pairs, workers=self.workers
        ):
            try:
                note_file, stat_file = book_dict["note_file"], book_dict["stat_file"]
                book_name = title_from_fname(note_file[0] or stat_file[0])
                book_type = get_book_type(note_file[0] or stat_file[0])
                with BookParser(book_type=book_type) as reader:
                    reader = (
                        reader.set_notes_fobj(note_file[1])
                        .set_stats_fobj(stat_file[1])
                        .set_book_name(book_name)
                    )
                    yield reader.build()
            except Exception:
                err_msg = "Exception occured when creating book object."
                logging.exception(err_msg)
