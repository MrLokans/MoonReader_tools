# coding: utf8
import unittest
from unittest.mock import patch

import os
import datetime

from MoonReader import *
# FB2_Note_Parser, AbstractNote, FB2_Note, MoonReaderStatistics, PDF_Note_Parser, PDF_Note, one_obj_or_list

SAMPLE_SHORT_TIMESTAMP = '1451686942'
SAMPLE_DATE = SAMPLE_SHORT_TIMESTAMP + '123'  # 1st January 2016 22:22:22


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
{date}


Some text 2
0
1
0
""".format(date=SAMPLE_DATE)
        self.sample_list = ['1', 'Title', 'test.pdf', 'test.pdf', '1', '1', '1', '1', '123123123', SAMPLE_DATE, '', '', 'Some Text', '0', '0', '1']

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
        self.assertEqual(note.time, datetime.datetime.fromtimestamp(int(SAMPLE_SHORT_TIMESTAMP)))

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


class TestPDFParserRoutines(unittest.TestCase):

    def test_notes_are_correctly_parsed(self):
        text = "245#A*#8#A1#1451496313379#A2#291#A3#301#A4#-256#A5#0#A6##A7# sample_text_1#A@##A*#9#A1#1451496349963#A2#4#A3#0#A4#-16711936#A5#0#A6##A7# sample_text_2#A@#"
        note_object = PDF_Note_Parser.from_text(text)

        self.assertEqual(len(note_object.notes), 2)
        self.assertEqual(note_object.notes[0].text, " sample_text_1")
        self.assertEqual(note_object.notes[1].text, " sample_text_2")

    def test_note_texts_splitted_correctly(self):
        pdf_text = "245#A*#<note_contents_1>#A@##A*#<note_contents_2>#A@#"
        note_texts = PDF_Note_Parser._find_note_text_pieces(text=pdf_text)
        self.assertEqual(len(note_texts), 2)
        self.assertEqual(note_texts[0], "#A*#<note_contents_1>#A@#")
        self.assertEqual(note_texts[1], "#A*#<note_contents_2>#A@#")

    def test_single_note_parses_correctly(self):
        note_text = "#A*#11#A1#1451497221825#A2#643#A3#646#A4#-11184811#A5#2#A6##A7#test_text#A@#"

        d = PDF_Note._dict_from_text(note_text)

        self.assertEqual(d.get("page", ""), "11")
        self.assertEqual(d.get("timestamp", ""), "1451497221825")
        self.assertEqual(d.get("color", ""), "-11184811")
        self.assertEqual(d.get("style", ""), "2")
        self.assertEqual(d.get("text", ""), "test_text")

    def test_note_inited_from_text_correctly(self):
        note_text = "#A*#11#A1#1451497221825#A2#643#A3#646#A4#-11184811#A5#2#A6##A7#test_text#A@#"

        note = PDF_Note.from_text(note_text)

        self.assertEqual(note.text, "test_text")
        self.assertEqual(note._timestamp, "1451497221825")
        self.assertEqual(note._color, "-11184811")
        self.assertEqual(note.modifier, AbstractNote.CROSSED)


class TestHelperMethods(unittest.TestCase):

    def test_binary_transform_int_list(self):
        seq1 = [0, 1, 0]
        bin_val = FB2_Note.modifier_from_seq(seq1)
        self.assertEqual(bin_val, 0b010)

    def test_binary_transform_str_list(self):
        seq1 = ["0", "1", "0"]
        bin_val = FB2_Note.modifier_from_seq(seq1)
        self.assertEqual(bin_val, 0b010)

    def test_one_or_list_returns_list_for_list_of_many_objects(self):
        l = [1, 2]
        self.assertEqual(one_obj_or_list(l), [1, 2])

    def test_one_or_list_returns_one_object_for_list_of_single_object(self):
        l = [100]
        self.assertEqual(one_obj_or_list(l), 100)


class TestStatistics(unittest.TestCase):

    def test_full_str_is_parsed_correctly(self):
        test_str = "1392540515970*15@0#6095:7.8%"
        po = MoonReaderStatistics.from_string(test_str)
        self.assertEqual(po.percentage, 7.8)
        self.assertEqual(po.pages, 15)
        self.assertEqual(po.uid, "1392540515970")


class TestColorExtractingRoutines(unittest.TestCase):

    def test_RGB_string_formed_correctly_from_RGBA_sequence(self):
        seq = ['0xff', '0xbb', '0xcc', '0xfe']
        s = rgb_string_from_hex(seq)
        self.assertEqual(s, '#BBCCFE')

    def test_RGB_string_formed_correctly_from_RGB_sequence(self):
        seq = ['0xbb', '0xcc', '0xfe']
        s = rgb_string_from_hex(seq)
        self.assertEqual(s, '#BBCCFE')

    def test_RGB_bytes_value_correctly_taken_from_positive_number(self):
        blue_color = 255  # 00 00 00 FF
        hexed = rgba_hex_from_int(blue_color)
        self.assertEqual(hexed, ['0x0', '0x0', '0x0', '0xff'])


class TestFileRoutines(unittest.TestCase):

    @patch('MoonReader.os.listdir')
    def test_correct_files_taken(self, patched_listdir):
        dir_name = "test"
        patched_listdir.return_value = ["test.an", "test.po", "..", ".", "unused_file.file", "no_ext_file"]
        files = get_moonreader_files(dir_name)
        self.assertEqual(list(sorted(files)), [os.path.join(dir_name, "test.an"), os.path.join(dir_name, "test.po")])

    def test_full_pairs_taken_correctly(self):
        files = ["test_book_1.po", "test_book_2.an", "test_book_2.po", "test_book_1.an"]
        pairs = get_same_book_files(files)
        self.assertEqual(pairs, [("test_book_1.an", "test_book_1.po"), ("test_book_2.an", "test_book_2.po")])

    def test_pairs_are_correctly_made_with_only_stat_file(self):
        files = ["test_book_1.po", "test_book_2.po"]
        pairs = get_same_book_files(files)
        self.assertEqual(pairs, [("", "test_book_1.po"), ("", "test_book_2.po")])

    def test_pairs_are_correctly_made_with_only_notes_file(self):
        files = ["test_book_1.an", "test_book_2.an"]
        pairs = get_same_book_files(files)
        self.assertEqual(pairs, [("test_book_1.an", ""), ("test_book_2.an", "")])

if __name__ == '__main__':
    unittest.main()
