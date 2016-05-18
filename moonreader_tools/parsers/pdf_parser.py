from moonreader_tools.parsers import BaseParser
from moonreader_tools.notes import PDFNote


class PDFNoteParser(BaseParser):
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
            start_pos = _text.find(PDFNoteParser.NOTE_START)
            end_pos = _text.find(PDFNoteParser.NOTE_END)
            if start_pos != -1 and end_pos != -1:
                note_len = len(PDFNoteParser.NOTE_END)
                note_text = _text[start_pos:end_pos + note_len]
                notes.append(note_text)
            else:
                break
            _text = _text[end_pos + len(PDFNoteParser.NOTE_END):]
        return notes

    @classmethod
    def _notes_from_note_texts(cls, note_texts):
        """Create note objects from text and return list"""
        return [PDFNote.from_text(text) for text in note_texts]
