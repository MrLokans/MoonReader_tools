"""
This class contains parsers of different moonreader note files
"""


import os
import zlib

from .conf import NOTE_EXTENSION
from .notes import PDF_Note, FB2_Note, EmptyNote


class EmptyBook(object):
    """This class presents an empty book object"""

    def __init__(self):
        self.book_id = 0
        self.notes = []


class PDF_Note_Parser(object):

    NOTE_START = "#A*#"
    NOTE_END = "#A@#"

    def __init__(self, note_id=None, notes=()):
        self.note_id = note_id
        self.notes = notes

    @classmethod
    def from_text(cls, text):
        """Creates PDF note class instance from string"""
        note_texts = cls._find_note_text_pieces(text)
        notes = cls._notes_from_note_texts(note_texts)
        return cls(note_id=None, notes=notes)

    @staticmethod
    def _find_note_text_pieces(text):
        """Splits notes text and return notes"""
        notes = []

        _text = text
        while _text:
            start_pos = _text.find(PDF_Note_Parser.NOTE_START)
            end_pos = _text.find(PDF_Note_Parser.NOTE_END)
            if start_pos != -1 and end_pos != -1:
                note_text = _text[start_pos:end_pos+len(PDF_Note_Parser.NOTE_END)]
                notes.append(note_text)
            else:
                break
            _text = _text[end_pos+len(PDF_Note_Parser.NOTE_END):]
        return notes

    @staticmethod
    def _notes_from_note_texts(note_texts):
        """Create note objects from text and return list"""
        return [PDF_Note.from_text(text) for text in note_texts]


class FB2_Note_Parser(object):
    NOTE_SPLITTER = '#'

    def __init__(self, note_id, notes):
        self.note_id = note_id
        self.notes = notes

    @classmethod
    def from_text(cls, text):
        """Creates FB2 note from text"""
        lines = text.splitlines()
        if len(lines) < 3:
            # TODO: rethink!
            return None
        _header, _note_lines = cls.split_note_text(lines)
        _id = 0 if _header[0] == '#' else int(_header[0])

        notes = [FB2_Note.from_str_list(l) for l in cls._notes_from_lines(_note_lines)]
        return cls(note_id=_id, notes=notes)

    @staticmethod
    def split_note_text(note_lines):
        """Splits note text into header and notes string"""
        header = note_lines[:3]
        note_text = note_lines[3:]
        return header, note_text

    @staticmethod
    def _notes_from_lines(lines):
        notes = []
        splitter_pos = []
        for i, tok in enumerate(lines):
            if tok == FB2_Note_Parser.NOTE_SPLITTER:
                splitter_pos.append(i)
        splitter_pos.append(len(lines))

        splitter_len = len(splitter_pos)
        for i, pos in enumerate(splitter_pos):
            if i < splitter_len-1:
                notes.append(lines[pos+1:splitter_pos[i+1]])
        return notes

    def _note_from_str_list(self, str_list):
        pass


class MoonReaderNotes(object):

    PARSE_STATEGIES = {
        'pdf': PDF_Note_Parser,
        'epub': FB2_Note_Parser,
        'fb2': FB2_Note_Parser,
    }

    # def __init__(self, id=id, notes=notes):
    #     self.id = id
    #     self.notes = notes

    @classmethod
    def from_file(cls, file_path):
        """Creates note object from filesystem path"""
        if not os.path.exists(file_path):
            return EmptyNote()
        assert os.path.exists(file_path)
        assert file_path.endswith(NOTE_EXTENSION)

        book_extension = file_path.split(".")[-2]
        if book_extension == "zip":
            book_extension = file_path.split(".")[-3]
        with open(file_path, 'rb') as f:
            return cls.from_file_obj(f, book_extension)

    @classmethod
    def from_file_obj(cls, flike_obj, ext):
        """Creates note object from file-like object"""
        if not flike_obj:
            return EmptyBook()
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
    def _from_string(cls, s, file_type="fb2"):
        """Creates note object from string"""
        return cls.PARSE_STATEGIES.get(file_type).from_text(s.decode())
