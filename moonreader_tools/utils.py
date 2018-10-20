"""
Module contains helper functions used across the library
"""

import os
import datetime
import struct
from typing import Tuple

from .conf import ALLOWED_TYPES, NOTE_EXTENSION, STAT_EXTENSION
from .errors import BookTypeError


def validate_book_ext(ext):
    allowed = ALLOWED_TYPES
    if ext.lower() not in allowed:
        msg = "Filetype ({}) is not supported. Supported types are: {}"
        raise BookTypeError(msg.format(ext, ", ".join(allowed)))


def title_from_fname(fname: str) -> str:
    """Extracts book title from file name"""
    fname = os.path.split(fname)[-1]
    if fname.endswith((".po", ".an")):
        fname = fname[:-3]
    if fname.endswith(".fb2.zip"):
        fname = fname[:-8]
    if fname.endswith((".fb2", ".pdf")):
        fname = fname[:-4]
    if fname.endswith(".epub"):
        fname = fname[:-5]
    return fname


def get_book_type(
    filename,
    default_type="",
    allowed_types=None,
    extensions=(NOTE_EXTENSION, STAT_EXTENSION),
):
    """Extracts book type (pdf, fb2) from extension.
    E.g. given filename my_book.fb2.zip fb2 will be returned"""
    if allowed_types is None:
        allowed_types = ALLOWED_TYPES
    if default_type:
        return default_type
    if not filename.endswith(extensions):
        err_msg = (
            "Only files that end with {0} are supported. " "filename provided: '{1}'"
        )
        raise BookTypeError(err_msg.format(", ".join(extensions), filename))
    splitted_title = filename.split(".")

    # Out book file should have at least two extensions
    # if default type is not specified
    if len(splitted_title) < 3:
        msg = "Incorrect filename, at least two extensions required: {}"
        raise BookTypeError(msg.format(filename))
    book_type = splitted_title[-2]

    validate_book_ext(book_type)

    is_zip_ext = book_type == "zip"
    if not is_zip_ext:
        # If not ends with .zip we check only if type is supported
        validate_book_ext(book_type)
    # if it ends with zip we should check whether it has extra extension
    # just before .zip

    elif is_zip_ext and len(splitted_title) > 2:
        # if preceding extension is allowed we return it
        allowed_ext = splitted_title[-3].lower() in ALLOWED_TYPES
        if allowed_ext:
            book_type = splitted_title[-3]
        else:
            book_type = "zip"
    # otherwise it is .zip file
    else:
        book_type = "zip"
    return book_type


def one_obj_or_list(seq):
    """If there is one object in list - return object, otherwise return list"""
    if len(seq) == 1:
        return seq[0]
    return seq


def get_moonreader_files(path):
    """Return sequence of MoonReader statistsics and note files
    in the given path"""
    files = (os.path.join(path, component) for component in os.listdir(path))
    return get_moonreader_files_from_filelist(files)


def get_moonreader_files_from_filelist(file_list):
    """Return sequence of MoonReader statistsics and note files
    in the given file list"""
    return (f for f in file_list if f.endswith((NOTE_EXTENSION, STAT_EXTENSION)))


def date_from_long_timestamp(str_timestamp: str) -> datetime.datetime:
    """Moonreader files utilize awkward timestamp version,
    so we trim it and calculate date"""
    return datetime.datetime.fromtimestamp(float(str_timestamp[:10]))


def color_tuple_from_overflowed_integer(number: int) -> Tuple[int, int, int, int]:
    """
    Internally we get the color stored as the overflowed
    signed integer, so we put it back into
    bytes representantion and extract color bytes
    (Opacity, Red, Green, Blue)
    """
    return struct.unpack("BBBB", struct.pack("i", number))  # type: ignore


def color_tuple_as_hex_code(color_tuple: Tuple[int, int, int, int]) -> str:
    """
    >>> color_tuple_as_hex_code((0, 255, 0, 255))
    >>> "#FF00FF"
    """
    return "#" + "".join(
        hex(byte_as_int).replace("0x", "") for byte_as_int in color_tuple[-3:]
    )


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
