"""
This module contains classes capable of parsing MoonReader's statistics files.
"""
import re
import os
from .conf import STAT_EXTENSION


class Statistics(object):
    _statistics_regex = """\
(^(?P<uid>[\d]+))\
(\*(?P<pages>[\d]+))\
(\@(?P<no1>[\d]+))?\
(#(?P<no2>[\d]+))?\
(:(?P<percentage>[\d.]+))%"""
    _compiled_regex = re.compile(_statistics_regex)

    def __init__(self, uid, pages, percentage, **kwargs):
        self.uid = uid
        self.pages = int(pages)
        self.percentage = float(percentage)

    @classmethod
    def from_file(cls, file_path):
        """Instantiates Statistics object from file path"""
        if not file_path or not os.path.exists(file_path):
            raise ValueError("File does not exist: {}".format(file_path))
        assert file_path.endswith(STAT_EXTENSION)

        with open(file_path, encoding="utf-8") as f:
            return cls.from_file_obj(f)

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
            return cls.empty_stats()
        items = match.groupdict()
        return cls(**items)

    @classmethod
    def empty_stats(cls):
        return cls(0, 0, 0)

    def is_empty(self):
        return self.uid == 0 and self.pages == 0 and self.percentage == 0
