import sys
import unittest
from unittest.mock import mock_open, patch

from moonreader_tools.conf import STAT_EXTENSION
from moonreader_tools.parsers import FB2NoteParser, PDFNoteParser, StatsAccessor
from tests.base import BaseTest


class TestPDFParserRoutines(BaseTest):
    def test_notes_are_correctly_parsed(self):
        text = "245#A*#8#A1#1451496313379#A2#291#A3#301#A4#-256#A5#0#A6##A7# sample_text_1#A@##A*#9#A1#1451496349963#A2#4#A3#0#A4#-16711936#A5#0#A6##A7# sample_text_2#A@#"
        notes = PDFNoteParser.from_text(text)

        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].text, " sample_text_1")
        self.assertEqual(notes[1].text, " sample_text_2")

    def test_note_texts_splitted_correctly(self):
        pdf_text = "245#A*#<note_contents_1>#A@##A*#<note_contents_2>#A@#"
        note_texts = PDFNoteParser._find_note_text_pieces(text=pdf_text)
        self.assertEqual(len(note_texts), 2)
        self.assertEqual(note_texts[0], "#A*#<note_contents_1>#A@#")
        self.assertEqual(note_texts[1], "#A*#<note_contents_2>#A@#")


class TestFB2ParserRoutines(BaseTest):
    def test_note_text_correctly_splitted_into_header_and_rest(self):
        header = self.generate_note_header()
        note_text = self.generate_note_text()
        note_content = header + note_text
        splitted_header, splitted_note_text = FB2NoteParser.split_note_text(
            note_content.splitlines()
        )
        self.assertEqual(header.splitlines(), splitted_header)
        self.assertEqual(note_text.splitlines(), splitted_note_text)

    def test_reads_raw_text_correctly(self):
        notes = FB2NoteParser.from_text(self.sample_note_text)

        self.assertEqual(len(notes), 2)
        note_1 = notes[0]

        self.assertEqual(note_1.text, "Some text")


class TestStatisticsParser(unittest.TestCase):
    def setUp(self):
        self.test_str = "1392540515970*15@0#6095:7.8%"

    def test_full_str_is_parsed_correctly(self):
        po = StatsAccessor.stats_from_string(self.test_str)
        self.assertEqual(po.percentage, 7.8)
        self.assertEqual(po.pages, 15)
        self.assertEqual(po.timestamp, "1392540515970")

    @patch("os.path.exists")
    def test_incorrect_files(self, path_exists_mock):
        path_exists_mock.return_value = True
        fname = "noextensionfile"
        with self.assertRaises(AssertionError):
            StatsAccessor.stats_from_file(fname)

    def test_empty_fname_raises_error(self):
        with self.assertRaises(ValueError):
            StatsAccessor.stats_from_file("")

    @patch("os.path.exists")
    @patch("__builtin__.open", mock_open(), create=True)
    @unittest.skipIf(int(sys.version[0]) > 2, "For python < 3")
    def test_empty_stats_return_for_empty_file_p3(self, path_exists_mock):
        path_exists_mock.return_value = True
        s = StatsAccessor.stats_from_file("aaaa" + STAT_EXTENSION)
        self.assertTrue(s.is_empty())
