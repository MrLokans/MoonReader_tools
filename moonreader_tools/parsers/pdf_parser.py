import re

from moonreader_tools.accessors.file_reader import FileReader
from moonreader_tools.notes import Note
from moonreader_tools.parsers.note_extractor import NoteExtractorMixin


class PDFNoteParser(FileReader, NoteExtractorMixin):
    # TODO: inherit from the basic object
    """Reads notes from PDF flike object"""
    NOTE_START = "#A*#"
    NOTE_END = "#A@#"
    PARSED_FORMAT = "PDF"

    SPLITTER_PATTERN = r"#A[0-9@\*]#"
    CORRESP_TABLE = (
        (0, "unknown_1"),
        (1, "page"),
        (2, "timestamp"),
        (3, "unknown_2"),  # Highlight start index?
        (4, "unknown_3"),  # Highlight end index?
        (5, "color"),
        (6, "style"),
        (7, "note"),
        (8, "text"),
        (9, None),
    )

    @classmethod
    def from_file_obj(cls, flike_obj):
        return cls.from_text(cls.read_file_obj(flike_obj))

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
            start_pos = _text.find(cls.NOTE_START)
            end_pos = _text.find(cls.NOTE_END)
            if start_pos != -1 and end_pos != -1:
                note_len = len(cls.NOTE_END)
                note_text = _text[start_pos : end_pos + note_len]
                notes.append(note_text)
            else:
                break
            _text = _text[end_pos + len(cls.NOTE_END) :]
        return notes

    @classmethod
    def _notes_from_note_texts(cls, note_texts):
        """Create note objects from text and return list"""
        return [cls.single_note_from_text(text) for text in note_texts]

    @classmethod
    def single_note_from_text(cls, text) -> Note:
        """Create note from text"""
        token_dict = cls._dict_from_text(text)
        return cls.note_from_dictionary(token_dict)

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
