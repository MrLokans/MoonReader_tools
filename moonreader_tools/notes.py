"""Collection of classes that present different book formats' notes"""
import datetime
import enum
from typing import Tuple

from moonreader_tools.utils import color_tuple_as_hex_code

DEFAULT_COLOR = (0, 255, 255, 255)


class NoteStyle(enum.Enum):
    SELECTED = "SELECTED"
    CROSSED_OUT = "CROSSED_OUT"
    STRAIGHT_UNDERLINE = "STRAIGHT_UNDERLINE"
    WAVEY_UNDERLINE = "WAVEY_UNDERLINE"
    DELETED = "DELETED"


class Note(object):
    """
    A simple DTO representing book note in the system
    """

    _REPR_TEXT_LENGTH = 100

    def __init__(
        self,
        text: str,
        created: datetime.datetime,
        style: NoteStyle = NoteStyle.SELECTED,
        color: Tuple[int, int, int, int] = DEFAULT_COLOR,
        note: str = "",
    ) -> None:
        self._text = text
        self._created = created
        self._style = style
        self._color = color
        self._note = note

    @property
    def color(self):
        return self._color

    @property
    def style(self):
        return self._style

    @property
    def text(self):
        return self._text

    @property
    def note(self):
        return self._note

    @property
    def created(self):
        return self._created

    def to_dict(self):
        return {
            "text": self.text,
            "note": self.note,
            "created": self.created.isoformat(),
            "style": self.style.value,
            "color": color_tuple_as_hex_code(self.color),
        }

    def __repr__(self):
        return "<Note: {}>".format(self.text[: self._REPR_TEXT_LENGTH])

    def __str__(self):
        return self.__repr__()
