import re

from moonreader_tools.accessors.base_accessor import BaseAccessor
from moonreader_tools.notes import Note
from moonreader_tools.utils import (
    date_from_long_timestamp,
    date_to_long_timestamp
)


class PDFAccessor(BaseAccessor):
    """Class, responsible for reading and writing notes
    to and from PDF files"""

    SUPPORTED_FORMATS = ('pdf', )

    NOTE_START = "#A*#"
    NOTE_END = "#A@#"
    PARSED_FORMAT = "PDF"

    SPLITTER_PATTERN = r"#A[0-9@\*]#"
    CORRESP_TABLE = (
        (0, 'unknown_1'),
        (1, "page"),
        (2, "timestamp"),
        (3, 'unknown_2'),
        (4, 'unknown_3'),
        (5, "color"),
        (6, "style"),
        (7, 'unknown_4'),
        (8, "text"),
        (9, None)
    )

    _DELIMETER_PATTERN = "#A{}#"
    _HEADER_SEQ = _DELIMETER_PATTERN.format("*")
    _FOOTER_SEQ = _DELIMETER_PATTERN.format("@")
    _SECTIONS_COUNT = 7

    STYLE_CORRESP = {
        "0": Note.MARKER,
        "1": Note.UNDERLINE,
        "2": Note.CROSSED,
        "3": Note.WAVED,
    }

    def __init__(self):
        pass

    def notes_from_file(self, filepath):
        """Read list of Note objects from the given file"""
        notes = []
        with open(filepath) as f:
            notes = self.from_text(f.read())
        return notes

    def notes_to_file(self, notes, filepath):
        """Dumps a sequence of Note object into the file"""
        # TODO: somehow handle ID variable
        _id = 0
        notes_text = "".join(self.note_to_string(n) for n in notes)
        with open(filepath, "w") as f:
            f.write(str(_id))
            f.write(notes_text)

    def from_text(self, text):
        """Creates PDF note class instance from string"""
        note_texts = self._find_note_text_pieces(text)
        notes = self._notes_from_note_texts(note_texts)
        return notes

    def _find_note_text_pieces(self, text):
        """Splits notes text and return notes"""
        notes = []

        _text = text
        while _text:
            start_pos = _text.find(self.NOTE_START)
            end_pos = _text.find(self.NOTE_END)
            if start_pos != -1 and end_pos != -1:
                note_len = len(self.NOTE_END)
                note_text = _text[start_pos:end_pos + note_len]
                notes.append(note_text)
            else:
                break
            _text = _text[end_pos + len(self.NOTE_END):]
        return notes

    def _notes_from_note_texts(self, note_texts):
        """Create note objects from text and return list"""
        return [self.note_from_text(text) for text in note_texts]

    def note_from_text(self, text):
        """Create note from text"""
        token_dict = self._dict_from_text(text)

        style = self._style_from_num_str(token_dict["style"])

        timestamp = token_dict.get("timestamp", "")

        created = date_from_long_timestamp(timestamp) if timestamp else None
        return Note(text=token_dict.get("text", ""), created=created,
                    style=style, color=token_dict.get("color", ""))

    @classmethod
    def _dict_from_text(cls, text):
        """Split note's text according to regex, and return fields"""

        note_tokens = re.split(cls.SPLITTER_PATTERN, text)
        assert len(note_tokens) > 8
        note_dict = {}
        for item in cls.CORRESP_TABLE:
            if not item[1]:
                continue
            note_dict[item[1]] = note_tokens[item[0]]
        return note_dict

    @classmethod
    def _style_from_num_str(cls, num_str):
        return cls.STYLE_CORRESP[num_str]

    def note_to_string(self, note):
        """Build string representation used by the e-book reader"""
        result = self._HEADER_SEQ
        # TODO: rewrite this method to be less hard-coded
        result += "0"

        result += self._DELIMETER_PATTERN.format(1)
        timestamp = note.created
        result += str(date_to_long_timestamp(timestamp))

        result += self._DELIMETER_PATTERN.format(2)
        result += "0"

        result += self._DELIMETER_PATTERN.format(3)
        result += "0"

        result += self._DELIMETER_PATTERN.format(4)
        result += note.color

        result += self._DELIMETER_PATTERN.format(5)
        result += str(note.modifier)
        result += self._DELIMETER_PATTERN.format(6)

        result += self._DELIMETER_PATTERN.format(7)
        result += note.text

        result += self._FOOTER_SEQ
        return result
