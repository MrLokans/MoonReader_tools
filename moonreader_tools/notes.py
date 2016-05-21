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
                 text="",
                 timestamp=None,
                 color=(),
                 modifier=0b0,
                 content="",
                 path=None,
                 path_lower=None
                 ):
        self.note_id = note_id
        self.text = text
        self._timestamp = timestamp
        self._content = content
        self._color = color
        self.modifier = modifier
        self.path = path
        self.path_lower = path_lower

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
        (7, 'unknown_4'),
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

    def __init__(self, text, timestamp, style, color, content=""):
        super(PDFNote, self).__init__(note_id=0,
                                      text=text,
                                      timestamp=timestamp,
                                      modifier=style,
                                      color=color,
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
        result = self._HEADER_SEQ
        # TODO: rewrite this method to be less hard-coded
        result += "0"

        result += self._DELIMETER_PATTERN.format(1)
        result += self._timestamp

        result += self._DELIMETER_PATTERN.format(2)
        result += "0"

        result += self._DELIMETER_PATTERN.format(3)
        result += "0"

        result += self._DELIMETER_PATTERN.format(4)
        result += self._color

        result += self._DELIMETER_PATTERN.format(5)
        result += str(self.modifier)
        result += self._DELIMETER_PATTERN.format(6)

        result += self._DELIMETER_PATTERN.format(7)
        result += self.text

        result += self._FOOTER_SEQ
        return result


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
        (8, 1, "color"),  # number, that shows the color styling has
        (9, 1, "timestamp"),  # integer, that shows when note was made
        (10, 2, "separator_space"),
        (12, 1, 'text'),  # actually, note's text
        (13, 3, 'modifier_bits'),  # is note deleted, e.g.
    ]

    def __init__(self, note_id,
                 text,
                 timestamp,
                 color,
                 modifier,
                 is_deleted=False,
                 content="",
                 path=None,
                 path_lower=None):
        super(FB2Note, self).__init__(note_id, text,
                                      timestamp,
                                      color,
                                      modifier,
                                      content=content,
                                      path=path,
                                      path_lower=path_lower)
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
        book_dict = {}
        is_deleted = False
        for item in cls.NOTE_SCHEME:
            if str_list[-1] == NOTE_DELETED:
                is_deleted = True
            book_dict[item[2]] = str_list[item[0]:item[0] + item[1]]
        return cls(note_id=one_obj_or_list(book_dict["note_id"]),
                   text=one_obj_or_list(book_dict["text"]),
                   timestamp=one_obj_or_list(book_dict["timestamp"]),
                   color=one_obj_or_list(book_dict["color"]),
                   modifier=cls.modifier_from_seq(book_dict["modifier_bits"]),
                   is_deleted=is_deleted,
                   content="\n".join(str_list),
                   path=one_obj_or_list(book_dict['book_path']),
                   path_lower=one_obj_or_list(book_dict['book_path_lower']))

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
        result += "{}\n".format(self.text)
        result += "{}\n".format(self.path)
        result += "{}\n".format(self.path_lower)

        # Fields with unknown purpose
        result += "0\n"
        result += "0\n"
        result += "0\n"
        result += "0\n"

        result += self._color + "\n"
        result += self._timestamp + "\n"

        result += "\n"
        result += "\n"

        result += self.text + "\n"
        result += "\n".join(self._number_to_binary_list(self.modifier))
        return result
