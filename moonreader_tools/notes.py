"""Collection of classes that present different book formats' notes"""

import re
import abc
import json
import datetime

from moonreader_tools.conf import NOTE_DELETED
from moonreader_tools.utils import date_from_long_timestamp, one_obj_or_list


class Note(object):

    CROSSED = 0b010
    MARKER = 0b0
    UNDERLINE = 0b100
    WAVED = 0b001

    def __init__(self, note_id=0, text="", created=None,
                 color="", modifier=0b0):
        """Creates note object
        :param note_id: ID of the note
        :type note_id: int or str
        :param text: note's text
        :type text: str
        :param created: when note was created
        :type created: datetime.datetime
        :param color: note's color
        :type: ???
        :param modifier: note's style (crossed, underlined, etc)
        :type modifier: int
        """
        self.id = str(note_id)
        self.text = text
        if created is None:
            self.created = datetime.datetime.now()
        else:
            self.created = created
        self.color = color
        self.modifier = modifier

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        d = {
            "id": self.id,
            "text": self.text,
            "created": str(self.created),
            "color": self.color
        }
        return d

    def __repr__(self):
        text = 'Note(id={}, text={}, created={})'
        return text.format(self.id, self.text, self.created)

    def __str__(self):
        return self.__repr__()


class AbstractNote(object):
    """Abstract class for all other note parsers"""

    __metaclass__ = abc.ABCMeta

    CROSSED = 0b010
    MARKER = 0b0
    UNDERLINE = 0b100
    WAVED = 0b001

    def __init__(self,
                 note_id=0,
                 text="",
                 timestamp=None,
                 color=(),
                 modifier=0b0,
                 content="",
                 path=None,
                 path_lower=None,
                 note=None,
                 title="",
                 last_chapter=0,
                 last_split_index=0,
                 last_position=0,
                 highlight_length=0,
                 highlight_color=0,
                 ):
        self.note_id = note_id
        self.text = text
        self._timestamp = timestamp
        self._content = content
        self._color = color
        self._highlight_color = highlight_color
        self.modifier = modifier
        self.path = path
        self.path_lower = path_lower
        self.title = title
        self.note = note
        self.last_chapter = last_chapter
        self.last_split_index = last_split_index
        self.last_position = last_position
        self.highlight_length = highlight_length

    @abc.abstractmethod
    def from_text(self, text):
        """Creates note object from text"""
        pass

    @property
    def time(self):
        return date_from_long_timestamp(self._timestamp)

    @classmethod
    def from_dict(cls, d):
        """Construct note object from dictionary"""
        return cls(**d)

    def to_dict(self):
        """Dump note to dictionary"""
        return {
            'text': self.text,
            'date': str(date_from_long_timestamp(self._timestamp)),
            'note': self.note,
        }

    def to_json(self):
        """Dump note to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @abc.abstractmethod
    def to_string(self):
        """Serialize note back to string, to be understood by
        e-book reader"""
        pass

    def save(self, notes_file):
        """Dumps notes into the file
        """
        with open(notes_file, "w") as f:
            f.write(notes_file)

    def _color_from_number(self):
        return self._color

    @classmethod
    def empty(cls):
        return cls(note_id=0,
                   text="",
                   timestamp=None,
                   modifier=0b0,
                   content="")

    def __str__(self):
        return '<Note: {}>'.format(self.text)


class PDFNote(AbstractNote):
    """Class, used to store and parse notes in the PDF format"""

    SPLITTER_PATTERN = r"#A[0-9@\*]#"
    CORRESP_TABLE = (
        (0, 'unknown_1'),
        (1, "page"),
        (2, "timestamp"),
        (3, 'unknown_2'),
        (4, 'unknown_3'),
        (5, "color"),
        (6, "style"),
        (7, "note"),
        (8, "text"),
        (9, None)
    )

    _DELIMETER_PATTERN = "#A{}#"
    _HEADER_SEQ = _DELIMETER_PATTERN.format("*")
    _FOOTER_SEQ = _DELIMETER_PATTERN.format("@")
    _SECTIONS_COUNT = 7

    STYLE_CORRESP = {
        "0": AbstractNote.MARKER,
        "1": AbstractNote.UNDERLINE,
        "2": AbstractNote.CROSSED,
        "3": AbstractNote.WAVED,
    }

    def __init__(self, text, timestamp, style, color, content="", note=""):
        super(PDFNote, self).__init__(note_id=0,
                                      text=text,
                                      timestamp=timestamp,
                                      modifier=style,
                                      color=color,
                                      note=note,
                                      content=content)

    @classmethod
    def from_text(cls, text):
        """Create note from text"""
        token_dict = cls._dict_from_text(text)

        style = cls._style_from_num_str(token_dict["style"])

        return cls(text=token_dict.get("text", ""),
                   timestamp=token_dict.get("timestamp", ""),
                   style=style,
                   color=token_dict.get("color", ""),
                   content=text,
                   note=token_dict.get("note", ""))

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

    def _get_delimiter(self, c: str) -> str:
        """
        Forms the delimiter substring with the given char
        """
        return self._DELIMETER_PATTERN.format(c)

    def to_string(self):
        """Build string representation used by the e-book reader"""
        result = self._HEADER_SEQ
        # TODO: rewrite this method to be less hard-coded
        result += "0"

        result += self._get_delimiter('1')
        result += self._timestamp

        result += self._get_delimiter('2')
        result += "0"

        result += self._get_delimiter('3')
        result += "0"

        result += self._get_delimiter('4')
        result += self._color

        result += self._get_delimiter('5')
        result += str(self.modifier)
        result += self._get_delimiter('6')
        result += self.note

        result += self._get_delimiter('7')
        result += self.text

        result += self._FOOTER_SEQ
        return result


class FB2Note(AbstractNote):
    """Class, used to store and parse notes in the FB2 format"""

    POSITION, LEN, NAME = range(3)

    NOTE_SCHEME = [
        # position, len, name
        (0, 1, 'note_id'),
        (1, 1, 'title'),
        (2, 1, 'path'),
        (3, 1, 'path_lower'),
        (4, 1, 'last_chapter'),
        (5, 1, 'last_split_index'),
        (6, 1, 'last_position'),
        (7, 1, 'highlight_length'),
        (8, 1, "color"),  # number, that shows the color styling has
        (9, 1, "timestamp"),  # integer, that shows when note was made
        (10, 2, "separator_space"),
        (11, 1, "note"),
        (12, 1, 'text'),  # actually, note's text
        (13, 3, 'modifier_bits'),  # is note deleted, e.g.
    ]

    def __init__(self, *args, is_deleted: bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_deleted = is_deleted

    @classmethod
    def from_text(cls, text: str) -> AbstractNote:
        """Returns note objects from parsed text"""
        lines = text.splitlines()
        return cls.from_str_list(lines)

    @classmethod
    def from_str_list(cls, str_list: list) -> AbstractNote:
        """In text file single note is presented as a sequence of lines,
        this method creates Note object from them"""
        book_dict = {}

        is_deleted = cls._is_deleted(str_list)

        for item in cls.NOTE_SCHEME:
            book_dict[item[cls.NAME]] = cls._extract_note_part(item, str_list)
        d = book_dict
        return cls(note_id=one_obj_or_list(d["note_id"]),
                   text=one_obj_or_list(d["text"]),
                   timestamp=one_obj_or_list(d["timestamp"]),
                   color=one_obj_or_list(d["color"]),
                   modifier=cls.modifier_from_seq(d["modifier_bits"]),
                   is_deleted=is_deleted,
                   content="\n".join(str_list),
                   path=one_obj_or_list(d['path']),
                   path_lower=one_obj_or_list(d['path_lower']),
                   note=one_obj_or_list(d['note']),
                   title=one_obj_or_list(d['title']),
                   last_chapter=one_obj_or_list(d['last_chapter']),
                   last_position=one_obj_or_list(d['last_position']),
                   last_split_index=one_obj_or_list(d['last_split_index']),
                   highlight_length=one_obj_or_list(d['highlight_length']),
                   )

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

    @classmethod
    def _is_deleted(cls, token_list):
        """
        Tries to find deleted flag
        """
        return token_list[-1] == NOTE_DELETED

    @staticmethod
    def modifier_from_seq(seq):
        """Transform a sequence of zeros and ones into binary number"""
        if seq[-1] == NOTE_DELETED:
            seq[-1] = 0
        return int("".join((str(x) for x in seq)), base=2)

    @classmethod
    def _number_to_binary_list(cls, number):
        """Turns number into list of binary
        digits from its binary representation.
        e.g. 4 will turn into ['1', '0', '0'] (0b100)
        """
        s_repr = "{:0>3b}".format(number)
        splitted = [c for c in s_repr]
        return splitted

    def to_string(self):
        """Build string representation used by the e-book reader"""
        result = ""

        # TODO: analyze how to treat not delimeters
        # result += "#\n"
        result += "{}\n".format(self.note_id)
        result += "{}\n".format(self.title)
        result += "{}\n".format(self.path)
        result += "{}\n".format(self.path_lower)

        # Fields with unknown purpose
        result += "{}\n".format(self.last_chapter)
        result += "{}\n".format(self.last_split_index)
        result += "{}\n".format(self.last_position)
        result += "{}\n".format(self.highlight_length)

        result += self._color + "\n"
        result += self._timestamp + "\n"

        result += "\n"
        result += "\n"

        result += self.text + "\n"
        result += "\n".join(self._number_to_binary_list(self.modifier))
        return result
