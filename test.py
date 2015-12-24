# coding: utf8
import unittest

from MoonReader import FB2_Note_Parser, AbstractNote, FB2_Note


class TestNoteReader(unittest.TestCase):

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
1441449604670


Some text 2
0
1
0
"""
        self.sample_list = ['1', 'Title', 'test.pdf', 'test.pdf', '1', '1', '1', '1', '123123123', '14700000000', '', '', 'Some Text', '0', '0', '1']

    def test_reads_raw_text_correctly(self):
        parser = FB2_Note_Parser(self.sample_note_text)

        self.assertEqual(len(parser.notes), 2)
        note_1 = parser.notes[0]

        self.assertEqual(note_1.text, "Some text")
        self.assertEqual(note_1.id, '2984')
        self.assertEqual(note_1.modifier, AbstractNote.MARKER)

    def test_fb2_note_creation_from_str_list_works(self):
        note = FB2_Note.from_str_list(self.sample_list)
        self.assertEqual(note.text, "Some Text")
        self.assertEqual(note.id, '1')
        self.assertEqual(note.time, '14700000000')

    def test_note_text_correctly_splitted_into_header_and_rest(self):
        header = self.generate_note_header()
        note_text = self.generate_note_text()
        note_content = header + note_text
        splitted_header, splitted_note_text = FB2_Note_Parser.split_note_text(note_content.splitlines())
        self.assertEqual(header.splitlines(), splitted_header)
        self.assertEqual(note_text.splitlines(), splitted_note_text)

    def test_fb2_note_from_list_has_correct_modifier(self):
        note = FB2_Note.from_str_list(self.sample_list)
        self.assertEqual(note.modifier, AbstractNote.WAVED)


class TestHelperMethods(unittest.TestCase):

    def test_binary_transform_int_list(self):
        seq1 = [0, 1, 0]
        bin_val = FB2_Note.modifier_from_seq(seq1)
        self.assertEqual(bin_val, 0b010)

    def test_binary_transform_str_list(self):
        seq1 = ["0", "1", "0"]
        bin_val = FB2_Note.modifier_from_seq(seq1)
        self.assertEqual(bin_val, 0b010)

if __name__ == '__main__':
    unittest.main()
