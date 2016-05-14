"""
This class contains parsers of different moonreader note files.
Every parser knows how to extrat notes from specifi vook file format
"""


import os
import abc
import zlib

from .conf import NOTE_EXTENSION
from .notes import PDF_Note, FB2_Note


class BaseParser(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def from_text(cls, text):
        """Parse given string and return a sequence of note objects"""
        pass


class PDF_Note_Parser(BaseParser):
    """Parser for PDF book format"""
    NOTE_START = "#A*#"
    NOTE_END = "#A@#"
    PARSED_FORMAT = "PDF"

    @classmethod
    def from_text(cls, text):
        """Creates PDF note class instance from string"""
        note_texts = cls._find_note_text_pieces(text)
        notes = cls._notes_from_note_texts(note_texts)
        return notes

    @classmethod
    def _find_note_text_pieces(cls, text):
        """Splits notes text and return notes"""
        notes = []

        _text = text
        while _text:
            start_pos = _text.find(PDF_Note_Parser.NOTE_START)
            end_pos = _text.find(PDF_Note_Parser.NOTE_END)
            if start_pos != -1 and end_pos != -1:
                note_len = len(PDF_Note_Parser.NOTE_END)
                note_text = _text[start_pos:end_pos + note_len]
                notes.append(note_text)
            else:
                break
            _text = _text[end_pos + len(PDF_Note_Parser.NOTE_END):]
        return notes

    @classmethod
    def _notes_from_note_texts(cls, note_texts):
        """Create note objects from text and return list"""
        return [PDF_Note.from_text(text) for text in note_texts]


class FB2_Note_Parser(BaseParser):
    """Parser for FB2 book format"""

    NOTE_SPLITTER = '#'
    PARSED_FORMAT = "FB2"

    @classmethod
    def from_text(cls, text):
        """Creates FB2 note from text"""
        lines = text.splitlines()
        if len(lines) < 3:
            # TODO: rethink!
            return None
        _header, _note_lines = cls.split_note_text(lines)
        text_chunks = cls._note_text_chunks(_note_lines)
        notes = [FB2_Note.from_text(text_chunk)
                 for text_chunk in text_chunks]
        return notes

    @staticmethod
    def split_note_text(note_lines):
        """Splits note text into header and notes string"""
        header = note_lines[:3]
        note_text = note_lines[3:]
        return header, note_text

    @classmethod
    def _note_text_chunks(cls, lines):
        """Accepts lines of text and splits them into
        separate chunks, each chunk containing lines belonging
        to the same note"""
        notes = []
        splitter_pos = []
        for i, tok in enumerate(lines):
            if tok == cls.NOTE_SPLITTER:
                splitter_pos.append(i)
        splitter_pos.append(len(lines))

        splitter_len = len(splitter_pos)
        for i, pos in enumerate(splitter_pos):
            if i < splitter_len - 1:
                notes.append("\n".join(lines[pos + 1:splitter_pos[i + 1]]))
        print(notes)
        return notes


class MoonReaderNotes(object):
    """
    Class, that defines what parsing strategy should be applied for the specified file.
    """

    PARSE_STATEGIES = {
        'pdf': PDF_Note_Parser,
        'epub': FB2_Note_Parser,
        'fb2': FB2_Note_Parser,
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
            raise ValueError("No flike object supplied!")
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
        strategy = cls.PARSE_STATEGIES.get(ext, None)
        if strategy is None:
            err_msg = "No known parsing startegy for {} format".format(ext)
            raise ValueError(err_msg)
        return strategy

    @classmethod
    def _from_string(cls, s, file_type="fb2"):
        """Creates note object from string"""
        strategy = cls._strategy_from_ext(file_type)
        return strategy.from_text(s.decode())
