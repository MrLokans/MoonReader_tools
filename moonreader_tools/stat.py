import re
from .conf import STAT_EXTENSION


class EmptyMoonReaderStatistics(object):

    def __init__(self):
        self.uid = 0
        self.pages = 0
        self.percentage = 0


class MoonReaderStatistics(object):
    # TODO: use verbose regexps
    _statistics_regex = r"(^(?P<uid>[\d]+))(\*(?P<pages>[\d]+))(\@(?P<no1>[\d]+))?(#(?P<no2>[\d]+))?(:(?P<percentage>[\d.]+))%"
    _compiled_regex = re.compile(_statistics_regex)

    def __init__(self, uid, pages, percentage, **kwargs):
        self.uid = uid
        self.pages = int(pages)
        self.percentage = float(percentage)

    @classmethod
    def from_file(cls, file_path):
        """Instantiates Statistics object from file path"""
        if not file_path:
            return None
        assert file_path.endswith(STAT_EXTENSION)

        with open(file_path, encoding="utf-8") as f:
            return cls.from_file_obj(f)

    @classmethod
    def from_file_obj(cls, flike_obj, ext=".po"):
        """Instantiates Statistics object from file object"""
        content = flike_obj.read()
        if isinstance(content, type(b'bytes')):
            content = content.decode('utf-8')
        if len(content) == 0:
            print("Statistics is empty.")
            return EmptyMoonReaderStatistics()
        return MoonReaderStatistics.from_string(content)

    @classmethod
    def from_string(cls, str_content):
        """Instantiates Statistics object from string"""
        match = MoonReaderStatistics._compiled_regex.match(str_content)
        if not match:
            return EmptyMoonReaderStatistics()
        items = match.groupdict()
        return MoonReaderStatistics(**items)
