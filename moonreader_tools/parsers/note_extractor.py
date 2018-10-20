import datetime
from typing import Tuple

from moonreader_tools import utils
from moonreader_tools.notes import Note, NoteStyle


DELETED_MARKER = "*DELETED*"


class NoteExtractorMixin(object):

    REQUIRED_FIELDS = {"text", "color", "timestamp", "style"}

    @staticmethod
    def extract_text(note_dict: dict) -> str:
        return utils.one_obj_or_list(note_dict["text"])

    @staticmethod
    def extract_color(note_dict: dict) -> Tuple[int, int, int, int]:
        color = int(utils.one_obj_or_list(note_dict["color"]))
        return utils.color_tuple_from_overflowed_integer(color)

    @staticmethod
    def extract_created(note_dict: dict) -> datetime.datetime:
        timestamp = utils.one_obj_or_list(note_dict["timestamp"])
        return utils.date_from_long_timestamp(timestamp)

    @staticmethod
    def extract_manual_note_text(note_dict: dict) -> datetime.datetime:
        return utils.one_obj_or_list(note_dict["note"])

    @staticmethod
    def extract_style(note_dict):
        style = note_dict["style"]
        if isinstance(style, list):
            if style[-1] == DELETED_MARKER:
                return NoteStyle.DELETED
        # FIXME: handle all of the other cases!
        # I don't have examples of other styles/modifiers applied
        # Perhaps I need to create a set of fake PDF books and
        # experiment with it later
        return NoteStyle.SELECTED

    @classmethod
    def note_from_dictionary(cls, note_dict: dict) -> Note:
        assert cls.REQUIRED_FIELDS < note_dict.keys(), (
            "Some of the required keys for the note are missing: "
            + str(cls.REQUIRED_FIELDS - note_dict.keys())
        )

        return Note(
            text=cls.extract_text(note_dict),
            created=cls.extract_created(note_dict),
            color=cls.extract_color(note_dict),
            style=cls.extract_style(note_dict),
            note=cls.extract_manual_note_text(note_dict),
        )
