import re


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
