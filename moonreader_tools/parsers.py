import os
import zlib

from .conf import NOTE_EXTENSION
from .notes import PDF_Note, FB2_Note


class PDF_Note_Parser(object):

    NOTE_START = "#A*#"
    NOTE_END = "#A@#"

    def __init__(self, id=None, notes=()):
        self.id = id
        self.notes = notes

    @staticmethod
    def from_text(text):
        note_texts = PDF_Note_Parser._find_note_text_pieces(text)
        notes = PDF_Note_Parser._notes_from_note_texts(note_texts)
        return PDF_Note_Parser(id=None, notes=notes)

    @staticmethod
    def _find_note_text_pieces(text):
        notes = []

        _text = text
        while(_text):
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
        return [PDF_Note.from_text(text) for text in note_texts]


class FB2_Note_Parser(object):
    NOTE_SPLITTER = '#'

    def __init__(self, id, notes):
        self.id = id
        self.notes = notes
        # self._note_text = note_text
        # self.parse_text()

    @staticmethod
    def from_text(text):
        lines = text.splitlines()
        if len(lines) < 3:
            # TODO: rethink!
            return None
        _header, _note_lines = FB2_Note_Parser.split_note_text(lines)
        _id = int(_header[0])
        # _indented = self._header[1]
        # _trimmed = self._header[2]

        notes = [FB2_Note.from_str_list(l) for l in FB2_Note_Parser._notes_from_lines(_note_lines)]
        return FB2_Note_Parser(id=_id, notes=notes)

    def parse_text(self):
        lines = self._note_text.splitlines()
        # for every note list there is always a header of 4 lines
        assert len(lines) > 3

        self._header, self._note_lines = FB2_Note_Parser.split_note_text(lines)
        self.id = int(self._header[0])
        self.indented = self._header[1]
        self.trimmed = self._header[2]

        self.notes = [FB2_Note.from_str_list(l) for l in FB2_Note_Parser._notes_from_lines(self._note_lines)]

    @staticmethod
    def split_note_text(note_lines):
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

    @staticmethod
    def from_file(file_path):
        content = ""
        assert file_path.endswith(NOTE_EXTENSION)
        assert os.path.exists(file_path)

        book_extension = file_path.split(".")[-2]
        if book_extension == "zip":
            book_extension = file_path.split(".")[-3]
        with open(file_path, 'rb') as f:
            content = f.read()
        if MoonReaderNotes._is_zipped(content):
            return MoonReaderNotes._from_zipped_string(content, file_type=book_extension)
        else:
            return MoonReaderNotes._from_string(content, file_type=book_extension)

    @staticmethod
    def _from_zipped_string(str_content, file_type="fb2"):
        if not MoonReaderNotes._is_zipped:
            raise ValueError("Given string is not zipped.")
        unpacked_str = MoonReaderNotes._unpack_str(str_content)
        return MoonReaderNotes._from_string(unpacked_str, file_type=file_type)

    @staticmethod
    def _unpack_str(zipped_str):
        return zlib.decompress(zipped_str)

    @staticmethod
    def _is_zipped(str_text):
        if len(str_text) < 2:
            return False
        return str_text[0], str_text[1] == '78', '9c'

    @staticmethod
    def _from_string(s, file_type="fb2"):
        return MoonReaderNotes.PARSE_STATEGIES.get(file_type).from_text(s.decode())
