"""Collection of classes that present different book formats' notes"""

import re
import abc
import json

from .conf import NOTE_DELETED
from .utils import date_from_long_timestamp, one_obj_or_list


class AbstractNote(object):
    """Abstract class for all other note parsers"""

    __metaclass__ = abc.ABCMeta

    CROSSED = 0b010
    MARKER = 0b0
    UNDERLINE = 0b100
    WAVED = 0b001

    def __init__(self,
                 note_id=0,
                 note_text="",
                 note_timestamp=None,
                 note_color=(),
                 note_modifier=0b0,
                 content=""
                 ):
        self.note_id = note_id
        self.text = note_text
        self._timestamp = note_timestamp
        self._content = content
        self._color = note_color
        self.modifier = note_modifier

    @abc.abstractmethod
    def from_text(self, text):
        """Creates note object from text"""
        pass

    @property
    def time(self):
        return date_from_long_timestamp(self._timestamp)

    def to_dict(self):
        """Dump note to dictionary"""
        return {
            'text': self.text,
            'date': str(date_from_long_timestamp(self._timestamp))
        }

    def to_json(self):
        """Dump note to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @abc.abstractmethod
    def to_string(self):
        """Serialize note back to string, to be understood by
        e-book reader"""
        pass

    def _color_from_number(self):
        return self._color

    @classmethod
    def empty(cls):
        return cls(note_id=0,
                   text="",
                   time=None,
                   modifier=0b0,
                   notes=[])

    def __str__(self):
        return '<Note: {}>'.format(self.text)


class PDFNote(AbstractNote):
    """Class, used to store and parse notes in the PDF format"""

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

    def __init__(self, text, timestamp, style, color, content=""):
        super(PDFNote, self).__init__(note_id=0,
                                      note_text=text,
                                      note_timestamp=timestamp,
                                      note_modifier=style,
                                      note_color=color,
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
                   content=text)

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

    def to_string(self):
        """Build string representation used by the e-book reader"""
        return ""


class FB2Note(AbstractNote):
    """Class, used to store and parse notes in the FB2 format"""

    NOTE_SCHEME = [
        # position, len, name
        (0, 1, 'note_id'),
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
        (13, 3, 'modifier_bits'),
    ]

    def __init__(self, note_id,
                 note_text,
                 note_timestamp,
                 note_color,
                 note_modifier,
                 is_deleted=False,
                 content=""):
        super(FB2Note, self).__init__(note_id, note_text,
                                      note_timestamp,
                                      note_color,
                                      note_modifier,
                                      content=content)
        self.is_deleted = is_deleted

    @classmethod
    def from_text(cls, text):
        """Returns note objects from parsed text"""
        lines = text.splitlines()
        return cls.from_str_list(lines)

    @classmethod
    def from_str_list(cls, str_list):
        """In text file single note is presented as a sequence of lines,
        this method creates Note object from them"""
        d = {}
        is_deleted = False
        for item in cls.NOTE_SCHEME:
            if str_list[-1] == NOTE_DELETED:
                is_deleted = True
            d[item[2]] = str_list[item[0]:item[0] + item[1]]
        return cls(note_id=one_obj_or_list(d["note_id"]),
                   note_text=one_obj_or_list(d["text"]),
                   note_timestamp=one_obj_or_list(d["timestamp"]),
                   note_color=one_obj_or_list(d["color"]),
                   note_modifier=cls.modifier_from_seq(d["modifier_bits"]),
                   is_deleted=is_deleted,
                   content="\n".join(str_list))

    @staticmethod
    def modifier_from_seq(seq):
        """Transform a sequence of zeros and ones into binary number"""
        if seq[-1] == NOTE_DELETED:
            seq[-1] = 0
        return int("".join((str(x) for x in seq)), base=2)

    def to_string(self):
        """Build string representation used by the e-book reader"""
        return ""
