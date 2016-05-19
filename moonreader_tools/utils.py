"""
Module contains different methods used across main classes
"""

import os
import struct
import datetime


from .conf import NOTE_EXTENSION, STAT_EXTENSION


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
    return (f for f in file_list
            if f.endswith((NOTE_EXTENSION, STAT_EXTENSION)))


def date_from_long_timestamp(str_timestamp):
    """Moonreader files utilize awkward timestamp version,
    so we trim it and calculate date"""
    return datetime.datetime.fromtimestamp(float(str_timestamp[:10]))


def rgba_hex_from_int(number):
    """Get bytes values from color integer."""
    number = int(number)
    # color is stored in overflowed integer representation (yeap, that's weird)
    byte_form = bytearray(struct.pack(">i", number))
    byte_values = (hex(x) for x in byte_form)
    return list(byte_values)


def rgb_string_from_hex(hex_seq):
    """Produce RGB string from bytes"""
    hex_seq = hex_seq[-3:]
    str_form = (x.replace('0x', '').upper() for x in hex_seq)
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
