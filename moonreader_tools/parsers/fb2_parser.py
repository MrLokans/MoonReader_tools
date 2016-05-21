from moonreader_tools.parsers import BaseParser
from moonreader_tools.notes import FB2Note


class FB2NoteParser(BaseParser):
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
        _, _note_lines = cls.split_note_text(lines)
        text_chunks = cls._note_text_chunks(_note_lines)
        notes = [FB2Note.from_text(text_chunk)
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
        return notes

