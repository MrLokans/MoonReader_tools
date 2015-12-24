import re
import os
import zlib


class AbstractNote(object):

    CROSSED = 0b010
    MARKER = 0b0
    UNDERLINE = 0b100
    WAVED = 0b001

    def __init__(self, note_id=0, note_text="", note_time=None, note_color=(), note_modifier=0b0):
        self.id = note_id
        self.text = note_text
        self.time = note_time
        self.color = note_color
        self.modifier = note_modifier


class PDF_Note_Parser(object):
    def __init__(self, text):
        pass


class PDF_Note(AbstractNote):
    pass


def one_obj_or_list(seq):
    """If there is one object in list - return object, either return list"""
    if len(seq) == 1:
        return seq[0]
    return seq


class FB2_Note(AbstractNote):

    NOTE_SCHEME = [
        # position, len, name
        (0, 1, 'id'),
        (1, 1, 'title'),
        (2, 1, 'book_path'),
        (3, 1, 'book_path_lower'),
        (4, 1, 'unknown_1'),
        (5, 1, 'unknown_2'),
        (6, 1, 'unknown_3'),
        (7, 1, 'unknown_4'),
        (8, 1, "color"),
        (9, 1, "timestamp"),
        (10, 2, "separator_space"),
        (12, 1, 'text'),
        (13, 3, 'modifier_bits')
    ]

    def __init__(self, note_id, note_text, note_time, note_color, note_modifier):
        super(FB2_Note, self).__init__(note_id, note_text,
                                       note_time, note_color, note_modifier)

    @staticmethod
    def from_str_list(str_list):
        d = {}
        for item in FB2_Note.NOTE_SCHEME:
            d[item[2]] = str_list[item[0]:item[0]+item[1]]
        return FB2_Note(note_id=one_obj_or_list(d["id"]),
                        note_text=one_obj_or_list(d["text"]),
                        note_time=one_obj_or_list(d["timestamp"]),
                        note_color=one_obj_or_list(d["color"]),
                        note_modifier=FB2_Note.modifier_from_seq(d["modifier_bits"])
                        )

    @staticmethod
    def modifier_from_seq(seq):
        return int("".join(map(str, seq)), base=2)


class FB2_Note_Parser(object):
    NOTE_SPLITTER = '#'

    def __init__(self, note_text):
        self._note_text = note_text
        self.parse_text()

    def parse_text(self):
        lines = self._note_text.splitlines()
        # for every note list there is always a header of 4 lines
        assert len(lines) > 3

        self._header, self._note_lines = FB2_Note_Parser.split_note_text(lines)
        self.book_id = int(self._header[0])
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
        "fb2": FB2_Note_Parser,
    }

    def __init__(self, notes):
        self.notes = notes

    @staticmethod
    def from_file(file_path):
        content = ""
        assert os.path.exists(file_path)
        with open(file_path, "wb") as f:
            content = f.read()
        if MoonReaderNotes._is_zipped(content):
            return MoonReaderNotes._from_zipped_string(content)
        else:
            return MoonReaderNotes._from_string(content)

    @staticmethod
    def _from_zipped_string(str_content):
        if not MoonReaderNotes._is_zipped:
            raise ValueError("Given string is not zipped.")

    @staticmethod
    def _unpack_str(zipped_str):
        return zlib.decompress(zipped_str)

    @staticmethod
    def _is_zipped(str_text):
        return len(str) > 2 and str_text[0], str_text[1] == '78', '9c'


class MoonReaderStatistics(object):

    _statistics_regex = r"(^(?P<uid>[\d]+))(\*(?P<pages>[\d]+))(\@(?P<no1>[\d]+))?(#(?P<no2>[\d]+))?(:(?P<percentage>[\d.]+))%"
    _compiled_regex = re.compile(_statistics_regex)

    def __init__(self, uid, pages, percentage, **kwargs):
        self.uid = uid
        self.pages = int(pages)
        self.percentage = float(percentage)

    @staticmethod
    def from_file(file_path):
        content = ""
        with open(file_path) as f:
            content = f.read()
        return MoonReaderStatistics.from_string(content)

    @staticmethod
    def from_string(str_content):
        match = MoonReaderStatistics._compiled_regex.match(str_content)
        if not match:
            raise ValueError("Incorrect string")
        items = match.groupdict()
        return MoonReaderStatistics(**items)


def main():
    pass

if __name__ == '__main__':
    main()
