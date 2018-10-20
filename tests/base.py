import unittest

SAMPLE_SHORT_TIMESTAMP = "1451686942"
SAMPLE_TIMESTAMP = SAMPLE_SHORT_TIMESTAMP + "123"  # 1st January 2016 22:22:22


class BaseTest(unittest.TestCase):
    def generate_note_header(self, id=1):
        return """\
{id}
indent:false
trim:false
""".format(
            id=id
        )

    def generate_note_text(
        self,
        id=1,
        text="test",
        path_1="test/test.pdf",
        path_2="test/test.pdf",
        title="test_title",
    ):
        return """\
{id}
{title}
{path_1}
{path_2}
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
""".format(
            **locals()
        )

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
""".format(
            date=SAMPLE_TIMESTAMP
        )

        self.sample_list = [
            "1",
            "Title",
            "test.pdf",
            "test.pdf",
            "1",
            "1",
            "1",
            "1",
            "123123123",
            SAMPLE_TIMESTAMP,
            "",
            "",
            "Some Text",
            "0",
            "0",
            "1",
        ]
        self.deleted_note_list = [
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "1436185081862",
            "",
            "0",
            "0",
            "0",
            "0",
            "*DELETED*",
        ]
