"""
Contains class responsible for Statistics object
reading and writing to files
"""
import io
import os
import re

from moonreader_tools.accessors.file_reader import FileReader
from moonreader_tools.conf import STAT_EXTENSION
from moonreader_tools.stat import Statistics


class StatsAccessor(FileReader):
    """
    Parse statistics file and return proper DTO
    """

    _STATISTICS_FORMAT = r"""
(^(?P<timestamp>[\d]+))     # When book was added to the shelf
(\*(?P<pages>[\d]+))        # total number of pages
(\@(?P<no1>[\d]+))?         # unknown field 1
(\#(?P<no2>[\d]+))?         # unknown field 1
(:(?P<percentage>[\d.]+))%  # ratio of already read pages
"""
    _STATISTICS_FORMAT_RE = re.compile(_STATISTICS_FORMAT, re.VERBOSE)

    @classmethod
    def stats_from_string(cls, text: str) -> Statistics:
        match = cls._STATISTICS_FORMAT_RE.match(text)
        if not match:
            raise ValueError("Statistics text cannot be analyzed.")
        items = match.groupdict()
        return Statistics(**items)

    @classmethod
    def stats_from_file_obj(cls, flike_obj) -> Statistics:
        content = cls.read_file_obj(flike_obj)
        if isinstance(content, type(b"bytes")):
            content = content.decode("utf-8")
        if len(content) == 0:
            return Statistics.empty_stats()
        return cls.stats_from_string(content)

    @classmethod
    def stats_from_file(cls, filename: str) -> Statistics:
        if not filename or not os.path.exists(filename):
            raise ValueError("File does not exist: {}".format(filename))
        assert filename.endswith(STAT_EXTENSION)

        with io.open(filename, encoding="utf-8") as stat_file:
            return cls.stats_from_file_obj(stat_file)
