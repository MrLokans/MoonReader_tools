import re
from .conf import STAT_EXTENSION


class MoonReaderStatistics(object):

    _statistics_regex = r"(^(?P<uid>[\d]+))(\*(?P<pages>[\d]+))(\@(?P<no1>[\d]+))?(#(?P<no2>[\d]+))?(:(?P<percentage>[\d.]+))%"
    _compiled_regex = re.compile(_statistics_regex)

    def __init__(self, uid, pages, percentage, **kwargs):
        self.uid = uid
        self.pages = int(pages)
        self.percentage = float(percentage)

    @staticmethod
    def from_file(file_path):
        if not file_path:
            return None
        assert file_path.endswith(STAT_EXTENSION)

        content = ""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        if len(content) == 0:
            # return MoonReaderStatistics()
            pass
        return MoonReaderStatistics.from_string(content)

    @staticmethod
    def from_string(str_content):
        match = MoonReaderStatistics._compiled_regex.match(str_content)
        if not match:
            # raise ValueError("Incorrect string")
            return None
        items = match.groupdict()
        return MoonReaderStatistics(**items)
