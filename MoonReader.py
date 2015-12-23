import re
import zlib


class PDF_Note_Parser(object):
    def __init__(self):
        pass


class MoonReaderNotes(object):

    def __init__(self):
        pass

    @staticmethod
    def from_file(file_path):
        content = ""
        with open(file_path, "wb") as f:
            content = f.read()
        if MoonReaderNotes._is_zipped(content):
            return MoonReaderNotes._from_zipped_string(content)
        else:
            return MoonReaderNotes._from_string(content)

    @staticmethod
    def _from_zipped_string(str_content):
        match = MoonReaderStatistics._compiled_regex.match(str_content)
        if not match:
            raise ValueError("Incorrect string")
        items = match.groupdict()
        return MoonReaderStatistics(**items)

    @staticmethod
    def _unpack_str(zipped_str):
        return zlib.decompress(zipped_str)

    @staticmethod
    def _is_zipped(str_text):
        return len(str) > 2 and str_text[0], str_text[1] == '78', '9c'


class MoonReaderStatistics(object):

    _statistics_regex = r"(^(?P<uid>[\d]+))(\*(?P<pages>[\d]+))(\@(?P<no1>[\d]+))?(#(?P<no2>[\d]+))?(:(?P<percentage>[\d.]+))%"
    _compiled_regex = re.compile(_statistics_regex)

    def __init__(self, uid, pages, percentage, **kwargs):
        self.uid = uid
        self.pages = pages
        self.percentage = percentage

    @staticmethod
    def from_file(file_path):
        content = ""
        with open(file_path) as f:
            content = f.read()
        return MoonReaderStatistics.from_string(content)

    @staticmethod
    def from_string(str_content):
        match = MoonReaderStatistics._compiled_regex.match(str_content)
        if not match:
            raise ValueError("Incorrect string")
        items = match.groupdict()
        return MoonReaderStatistics(**items)


def main():
    test_str = "1392540515970*15@0#6095:7.8%"
    po = MoonReaderStatistics.from_string(test_str)

    print po.percentage
    print po.pages
    print po.uid

if __name__ == '__main__':
    main()
