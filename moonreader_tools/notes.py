import re

from .utils import date_from_long_timestamp, one_obj_or_list


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
