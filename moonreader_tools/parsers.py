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
