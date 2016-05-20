"""
This module contains classes capable of parsing MoonReader's statistics files.
"""
import re
import os
from .conf import STAT_EXTENSION


class Statistics(object):
    """Class responsible for statistics data parsing, storage
and, in future releases, writing"""
    _statistics_regex = r"""
(^(?P<timestamp>[\d]+))     # When book was added to the shelf
(\*(?P<pages>[\d]+))        # total number of pages
(\@(?P<no1>[\d]+))?         # unknown field 1
(\#(?P<no2>[\d]+))?         # unknown field 1
(:(?P<percentage>[\d.]+))%  # ratio of already read pages
"""
    _compiled_regex = re.compile(_statistics_regex, re.VERBOSE)

    def __init__(self, timestamp, pages, percentage, **kwargs):
        self.timestamp = timestamp
        self.pages = int(pages)
        self.percentage = float(percentage)
        self._rest = kwargs

    @classmethod
    def from_file(cls, file_path):
        """Instantiates Statistics object from file path"""
        if not file_path or not os.path.exists(file_path):
            raise ValueError("File does not exist: {}".format(file_path))
        assert file_path.endswith(STAT_EXTENSION)

        with open(file_path, encoding="utf-8") as stat_file:
            return cls.from_file_obj(stat_file)

    @classmethod
    def from_file_obj(cls, flike_obj):
        """Instantiates Statistics object from file object"""
        content = flike_obj.read()
        if isinstance(content, type(b'bytes')):
            content = content.decode('utf-8')
        if len(content) == 0:
            print("Statistics is empty.")
            return cls.empty_stats()
        return cls.from_string(content)

    @classmethod
    def from_string(cls, str_content):
        """Instantiates Statistics object from string"""
        match = cls._compiled_regex.match(str_content)
        if not match:
            raise ValueError("Note content cannot be analyzed.")
            # return cls.empty_stats()
        items = match.groupdict()
        return cls(**items)

    @classmethod
    def empty_stats(cls):
        """Returns empty statistics object."""
        return cls(0, 0, 0)

    def is_empty(self):
        """Checks whether the statistics object is with empty
statistics data."""
        return self.timestamp == 0 and self.pages == 0 and self.percentage == 0

    def to_string(self):
        """Creates string representation of the object,
        ready to be saved into the file"""
        result = ""
        result += str(self.timestamp)
        result += "*"

        result += str(self.pages)
        result += ":"

        result += str(self.percentage) + "%"
        return result

    def to_file(self, filepath):
        """Dumps statistics object to file that
        can be read by moonreader"""
        with open(filepath) as f_out:
            f_out.write(self.to_string())
