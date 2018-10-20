from typing import List

from moonreader_tools.accessors.file_reader import FileReader
from moonreader_tools.notes import Note
from moonreader_tools.parsers.note_extractor import NoteExtractorMixin


class FB2NoteParser(FileReader, NoteExtractorMixin):
    # TODO: Inherit from the base class
    """Parser for FB2 book format"""

    NOTE_SPLITTER = "#"
    PARSED_FORMAT = "FB2"

    POSITION, LEN, NAME = range(3)

    NOTE_SCHEME = [
        # position, len, name
        (0, 1, "note_id"),
        (1, 1, "title"),
        (2, 1, "path"),
        (3, 1, "path_lower"),
        (4, 1, "last_chapter"),
        (5, 1, "last_split_index"),
        (6, 1, "last_position"),
        (7, 1, "highlight_length"),
        (8, 1, "color"),  # number, that shows the color styling has
        (9, 1, "timestamp"),  # integer, that shows when note was made
        (10, 1, "separator_space"),
        (11, 1, "note"),
        (12, 1, "text"),  # actually, note's text
        (13, 3, "style"),  # is note deleted, e.g.
    ]

    @classmethod
    def from_file_obj(cls, flike_obj) -> List[Note]:
        return cls.from_text(cls.read_file_obj(flike_obj))

    @classmethod
    def from_text(cls, text: str) -> List[Note]:
        """Creates FB2 note from text"""
        lines = text.splitlines()
        if len(lines) < 3:
            raise ValueError("Incorrect FB2 notes text")
        _, _note_lines = cls.split_note_text(lines)
        text_chunks = cls._note_text_chunks(_note_lines)
        notes = [cls.single_note_from_text(text_chunk) for text_chunk in text_chunks]
        return notes

    @classmethod
    def single_note_from_text(cls, text_chunk: str) -> Note:
        """Returns note objects from parsed text"""
        lines = text_chunk.splitlines()
        return cls.from_str_list(lines)

    @classmethod
    def from_str_list(cls, str_list: list) -> Note:
        """In text file single note is presented as a sequence of lines,
        this method creates Note object from them"""
        book_dict = {}
        for item in cls.NOTE_SCHEME:
            book_dict[item[cls.NAME]] = cls._extract_note_part(item, str_list)
        return cls.note_from_dictionary(book_dict)

    @classmethod
    def _extract_note_part(cls, item_part, token_list):
        """
        Extracts the given part from the note
        token list

        :param item_part: element from the NOTE_SCHEME
        :type item_part: tuple
        :param token_list: list of note tokens
        """
        _start = item_part[cls.POSITION]
        _end = item_part[cls.POSITION] + item_part[cls.LEN]
        return token_list[_start:_end]

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
                notes.append("\n".join(lines[pos + 1 : splitter_pos[i + 1]]))
        return notes
