"""
This class contains parsers of different moonreader note files.
Every parser knows how to extrat notes from specifi vook file format
"""


import os
import zlib

from moonreader_tools.parsers import (
    FB2NoteParser,
    PDFNoteParser
)
from moonreader_tools.conf import NOTE_EXTENSION


class MoonReaderNotes(object):
    """
    Class, that defines what parsing strategy should be applied
    for the specified file.
    """

    PARSE_STATEGIES = {
        'pdf': PDFNoteParser,
        'epub': FB2NoteParser,
        'fb2': FB2NoteParser,
    }

    @classmethod
    def from_file(cls, file_path):
        """Creates note object from filesystem path"""
        if not os.path.exists(file_path):
            return []
        assert os.path.exists(file_path)
        assert file_path.endswith(NOTE_EXTENSION)

        book_extension = file_path.split(".")[-2]
        if book_extension == "zip":
            book_extension = file_path.split(".")[-3]
        with open(file_path, 'rb') as book_notes_f:
            return cls.from_file_obj(book_notes_f, book_extension)

    @classmethod
    def from_file_obj(cls, flike_obj, ext):
        """Creates note object from file-like object"""
        if not flike_obj:
            return None
            # raise ValueError("No flike object supplied!")
        content = flike_obj.read()
        if cls._is_zipped(content):
            return cls._from_zipped_string(content, file_type=ext)
        else:
            return cls._from_string(content, file_type=ext)

    @classmethod
    def _from_zipped_string(cls, str_content, file_type="fb2"):
        """Creates note object from zip-compressed string"""
        if not cls._is_zipped:
            raise ValueError("Given string is not zipped.")
        unpacked_str = cls._unpack_str(str_content)
        return cls._from_string(unpacked_str, file_type=file_type)

    @staticmethod
    def _unpack_str(zipped_str):
        """Decompresses zipped string"""
        return zlib.decompress(zipped_str)

    @staticmethod
    def _is_zipped(str_text):
        """Checks whether given sequence is compressed with zip"""
        if len(str_text) < 2:
            return False
        return (str_text[0], str_text[1]) == (int('78', base=16), int('9c', base=16))

    @classmethod
    def _strategy_from_ext(cls, ext):
        """Chooses parsing strategies depending on the file extension"""
        strategy = cls.PARSE_STATEGIES.get(ext, None)
        if strategy is None:
            err_msg = "No known parsing startegy for {} format".format(ext)
            raise ValueError(err_msg)
        return strategy

    @classmethod
    def _from_string(cls, line, file_type="fb2"):
        """Creates note object from string"""
        strategy = cls._strategy_from_ext(file_type)
        return strategy.from_text(line.decode())
