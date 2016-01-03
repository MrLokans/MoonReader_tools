import unittest

SAMPLE_SHORT_TIMESTAMP = '1451686942'
SAMPLE_DATE = SAMPLE_SHORT_TIMESTAMP + '123'  # 1st January 2016 22:22:22


class BaseTest(unittest.TestCase):

    def generate_note_header(self, id=1):
        return """\
{id}
indent:false
trim:false
""".format(id=id)

    def generate_note_text(self, id=1, text="test", title="test_title"):
        return """\
{id}
{title}
/test/test/test.pdf
/test/test/test.pdf
0
0
0
0
0
0


{text}
0
0
0
""".format(**locals())

    def generate_file_content(self, id=1, notes_count=1):
        header = self.generate_note_header(id=id)
        notes = "\n".join(self.generate_note_text(i) for i in range(notes_count))
        return header + notes

    def setUp(self):
        self.sample_note_text = """\
343599
indent:false
trim:false
#
2984
Sample book title
/sdcard/Books/MoonReader/Book.fb2.zip
/sdcard/books/moonreader/book.fb2.zip
2
0
222
131
-16711936
1441449604670


Some text
0
0
0
#
2985
Another book title
/sdcard/Books/MoonReader/Book2.fb2.zip
/sdcard/books/moonreader/book2.fb2.zip
2
0
222
131
-16711936
{date}


Some text 2
0
1
0
""".format(date=SAMPLE_DATE)
        self.sample_list = ['1', 'Title', 'test.pdf', 'test.pdf', '1', '1', '1', '1', '123123123', SAMPLE_DATE, '', '', 'Some Text', '0', '0', '1']