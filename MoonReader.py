import re
import os
import io
import abc
import zlib
import struct
import json
import datetime

NOTE_EXTENSION = ".an"
STAT_EXTENSION = ".po"

# TODO: handle *DELETED* end tag!


def one_obj_or_list(seq):
    """If there is one object in list - return object, either return list"""
    if len(seq) == 1:
        return seq[0]
    return seq


def get_moonreader_files(path):
    files = map(lambda x: os.path.join(path, x), os.listdir(path))
    return filter(lambda x: x.endswith((NOTE_EXTENSION, STAT_EXTENSION)), files)


def date_from_long_timestamp(str_timestamp):
    return datetime.datetime.fromtimestamp(float(str_timestamp[:10]))


def rgba_hex_from_int(number):
    number = int(number)
    # color is stored in overflowed integer representation (yeap, that's weird)
    byte_form = struct.pack(">i", number)
    byte_values = map(hex, byte_form)
    return list(byte_values)


def rgb_string_from_hex(hex_seq):
    hex_seq = hex_seq[-3:]
    str_form = map(lambda x: x.replace('0x', '').upper(), hex_seq)
    return '#' + "".join(str_form)


def get_same_book_files(files):
    """Returns pairs of files that belong to the same book"""
    pairs = []
    files = list(files)
    files_set = set(files)
    for fname in files:
        if fname not in files_set:
            continue
        if fname.endswith(NOTE_EXTENSION):
            pair_fname = os.path.splitext(fname)[0] + STAT_EXTENSION
            if pair_fname in files_set:
                pairs.append((fname, pair_fname))
                files_set.remove(fname)
                files_set.remove(pair_fname)
            else:
                pairs.append((fname, ""))
                files_set.remove(fname)
        elif fname.endswith(STAT_EXTENSION):
            pair_fname = os.path.splitext(fname)[0] + NOTE_EXTENSION
            if pair_fname in files_set:
                pairs.append((pair_fname, fname))
                files_set.remove(fname)
                files_set.remove(pair_fname)
            else:
                pairs.append(("", fname))
                files_set.remove(fname)
    return pairs


class AbstractNote(object):

    CROSSED = 0b010
    MARKER = 0b0
    UNDERLINE = 0b100
    WAVED = 0b001

    def __init__(self, note_id=0, note_text="", note_timestamp=None, note_color=(), note_modifier=0b0):
        self.id = note_id
        self.text = note_text
        self._timestamp = note_timestamp
        self._color = note_color
        self.modifier = note_modifier

    @property
    def time(self):
        return date_from_long_timestamp(self._timestamp)

    def _color_from_number(self):
        return self._color


class AbstractBookNotes(object):

    def __init__(self, id, notes):
        self.id = id
        self.notes = notes


class Abstract_Note_Parser(abc.ABCMeta):

    @abc.abstractmethod
    def from_text(txt):
        pass


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


class PDF_Note(AbstractNote):

    SPLITTER_PATTERN = r"#A[0-9@\*]#"
    CORRESP_TABLE = (
        (0, None),
        (1, "page"),
        (2, "timestamp"),
        (3, None),
        (4, None),
        (5, "color"),
        (6, "style"),
        (7, None),
        (8, "text"),
        (9, None)
    )

    STYLE_CORRESP = {
        "0": AbstractNote.MARKER,
        "1": AbstractNote.UNDERLINE,
        "2": AbstractNote.CROSSED,
        "3": AbstractNote.WAVED,
    }

    def __init__(self, text, timestamp, style, color):
        super(PDF_Note, self).__init__(note_id=0,
                                       note_text=text,
                                       note_timestamp=timestamp,
                                       note_modifier=style,
                                       note_color=color)

    @staticmethod
    def from_text(text):
        token_dict = PDF_Note._dict_from_text(text)

        style = PDF_Note._style_from_num_str(token_dict["style"])

        return PDF_Note(text=token_dict.get("text", ""),
                        timestamp=token_dict.get("timestamp", ""),
                        style=style,
                        color=token_dict.get("color", ""))

    @staticmethod
    def _dict_from_text(text):
        """Split note's text according to regex, and return fields"""

        note_tokens = re.split(PDF_Note.SPLITTER_PATTERN, text)
        assert len(note_tokens) > 8
        d = {}
        for item in PDF_Note.CORRESP_TABLE:
            if not item[1]:
                continue
            d[item[1]] = note_tokens[item[0]]
        return d

    @staticmethod
    def _style_from_num_str(num_str):
        return PDF_Note.STYLE_CORRESP[num_str]


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

    def __init__(self, note_id, note_text, note_timestamp, note_color, note_modifier):
        super(FB2_Note, self).__init__(note_id, note_text,
                                       note_timestamp, note_color, note_modifier)

    @staticmethod
    def from_str_list(str_list):
        d = {}
        for item in FB2_Note.NOTE_SCHEME:
            d[item[2]] = str_list[item[0]:item[0]+item[1]]
        return FB2_Note(note_id=one_obj_or_list(d["id"]),
                        note_text=one_obj_or_list(d["text"]),
                        note_timestamp=one_obj_or_list(d["timestamp"]),
                        note_color=one_obj_or_list(d["color"]),
                        note_modifier=FB2_Note.modifier_from_seq(d["modifier_bits"])
                        )

    @staticmethod
    def modifier_from_seq(seq):
        """Transform a sequence of zeros and ones into binary number"""
        return int("".join(map(str, seq)), base=2)


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


class MoonReaderStatistics(object):

    _statistics_regex = r"(^(?P<uid>[\d]+))(\*(?P<pages>[\d]+))(\@(?P<no1>[\d]+))?(#(?P<no2>[\d]+))?(:(?P<percentage>[\d.]+))%"
    _compiled_regex = re.compile(_statistics_regex)

    def __init__(self, uid, pages, percentage, **kwargs):
        self.uid = uid
        self.pages = int(pages)
        self.percentage = float(percentage)

    @staticmethod
    def from_file(file_path):
        if not file_path:
            return None
        assert file_path.endswith(STAT_EXTENSION)

        content = ""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        if len(content) == 0:
            # return MoonReaderStatistics()
            pass
        return MoonReaderStatistics.from_string(content)

    @staticmethod
    def from_string(str_content):
        match = MoonReaderStatistics._compiled_regex.match(str_content)
        if not match:
            # raise ValueError("Incorrect string")
            return None
        items = match.groupdict()
        return MoonReaderStatistics(**items)


class MoonReaderBookData(object):

    def __init__(self, stats, notes):
        self.stats = stats
        self.notes = notes

    def to_json(self):
        return {}

    @staticmethod
    def _from_file_tuple(tpl):
        stat_file, note_file = tpl
        return MoonReaderBookData(MoonReaderStatistics.from_file(note_file),
                                  MoonReaderNotes.from_file(stat_file))


def main():
    temp_dir = '/home/anders-lokans/Dropbox/Books/.Moon+/Cache'
    files = get_moonreader_files(temp_dir)
    tuples = get_same_book_files(files)
    print([MoonReaderBookData._from_file_tuple(x) for x in tuples])

if __name__ == '__main__':
    main()
