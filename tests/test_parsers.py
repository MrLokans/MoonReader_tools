import zlib
import sys
import unittest

try:
    from unittest.mock import patch, mock_open
except ImportError:
    from mock import patch, mock_open


from moonreader_tools.parsers import (
    PDFNoteParser,
    FB2NoteParser,
    MoonReaderNotes
)
from moonreader_tools.stat import Statistics

from moonreader_tools.notes import AbstractNote
from moonreader_tools.conf import STAT_EXTENSION

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
        splitted_header, splitted_note_text = FB2NoteParser.split_note_text(note_content.splitlines())
        self.assertEqual(header.splitlines(), splitted_header)
        self.assertEqual(note_text.splitlines(), splitted_note_text)

    def test_reads_raw_text_correctly(self):
        notes = FB2NoteParser.from_text(self.sample_note_text)

        self.assertEqual(len(notes), 2)
        note_1 = notes[0]

        self.assertEqual(note_1.text, "Some text")
        self.assertEqual(note_1.note_id, '2984')
        self.assertEqual(note_1.modifier, AbstractNote.MARKER)


class TestStatisticsParser(unittest.TestCase):

    def setUp(self):
        self.test_str = "1392540515970*15@0#6095:7.8%"

    def test_full_str_is_parsed_correctly(self):
        po = Statistics.from_string(self.test_str)
        self.assertEqual(po.percentage, 7.8)
        self.assertEqual(po.pages, 15)
        self.assertEqual(po.timestamp, "1392540515970")

    def test_stat_dumps_to_string_correctly(self):
        po = Statistics(timestamp="1392540515970", pages=20, percentage=20.3)
        s = po.to_string()

        dumped = Statistics.from_string(s)
        self.assertEqual(dumped.percentage, 20.3)
        self.assertEqual(dumped.pages, 20)
        self.assertEqual(dumped.timestamp, "1392540515970")

    @patch('os.path.exists')
    def test_incorrect_files(self, path_exists_mock):
        path_exists_mock.return_value = True
        fname = "noextensionfile"
        with self.assertRaises(AssertionError):
            Statistics.from_file(fname)

    def test_empty_fname_raises_error(self):
        with self.assertRaises(ValueError):
            Statistics.from_file("")

    @patch('os.path.exists')
    @patch('__builtin__.open', mock_open(), create=True)
    @unittest.skipIf(int(sys.version[0]) > 2, "For python < 3")
    def test_empty_stats_return_for_empty_file_p3(self,
                                                  path_exists_mock):
        path_exists_mock.return_value = True
        s = Statistics.from_file("aaaa" + STAT_EXTENSION)
        self.assertTrue(s.is_empty())

    @unittest.skipIf(int(sys.version[0]) < 3, "For python > 3.0")
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_empty_stats_return_for_empty_file_p2(self,
                                                  open_mock, path_exists_mock):
        open_mock.read.return_value = ""
        path_exists_mock.return_value = True
        s = Statistics.from_file("aa" + STAT_EXTENSION)
        self.assertTrue(s.is_empty())

    @patch('os.path.exists')
    @patch('__builtin__.open', mock_open(), create=True)
    @unittest.skipIf(int(sys.version[0]) > 2, "For python < 3")
    def text_correctly_reads_from_file_p3(self, exists_mock, open_mock):
        open_mock.read.return_value = self.test_str
        exists_mock.return_value = True
        s = Statistics.from_file("aa" + STAT_EXTENSION)
        self.assertEqual(s.percentage, 7.8)
        self.assertEqual(s.pages, 15)
        self.assertEqual(s.uid, "1392540515970")

    @patch('os.path.exists')
    @patch('builtins.open')
    @unittest.skipIf(int(sys.version[0]) < 3, "For python > 3.0")
    def text_correctly_reads_from_file_p2(self, exists_mock, open_mock):
        open_mock.read.return_value = self.test_str
        exists_mock.return_value = True
        s = Statistics.from_file("aa" + STAT_EXTENSION)
        self.assertEqual(s.percentage, 7.8)
        self.assertEqual(s.pages, 15)
        self.assertEqual(s.uid, "1392540515970")


class TestMoonReaderNotes(unittest.TestCase):

    def test_correctly_unpacks_zipped_str(self):
        sample_s = b"12312412412adf2qe12d-ascacafq5"
        zipped = zlib.compress(sample_s)
        self.assertEqual(MoonReaderNotes._unpack_str(zipped), sample_s)

    def test_correctly_determines_zipped_str(self):
        zipped = [int('78', base=16), int('9c', base=16), int('aa', base=16), int('ff', base=16)]
        self.assertTrue(MoonReaderNotes._is_zipped(zipped))

    def test_correctly_determines_not_zipped(self):
        sample_s = "12312412412adf2qe12d-ascacafq5"
        self.assertFalse(MoonReaderNotes._is_zipped(sample_s))

    def test_correctly_determines_short_str(self):
        sample_s = "78".encode('utf-8')
        self.assertFalse(MoonReaderNotes._is_zipped(sample_s))

    @patch('os.path.exists')
    def test_returns_empty_note_for_non_existent_path(self, mocked_exists):
        mocked_exists.return_value = False
        notes = MoonReaderNotes.from_file("a")
        self.assertEqual(notes, [])


class TestGenericParsers(unittest.TestCase):

    def test_return_correct_strategy(self):
        p = MoonReaderNotes._strategy_from_ext("pdf")
        f = MoonReaderNotes._strategy_from_ext("fb2")
        self.assertTrue(p.PARSED_FORMAT, "PDF")
        self.assertTrue(f.PARSED_FORMAT, "FB2")
        with self.assertRaises(ValueError):
            MoonReaderNotes._strategy_from_ext(".unknown")

    def test_correctly_parses_string(self):
        s = "245#A*#8#A1#1451496313379#A2#291#A3#301#A4#-256#A5#0#A6##A7# sample_text_1#A@##A*#9#A1#1451496349963#A2#4#A3#0#A4#-16711936#A5#0#A6##A7# sample_text_2#A@#".encode('utf-8')
        notes = MoonReaderNotes._from_string(s, file_type="pdf")

        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].text, " sample_text_1")
        self.assertEqual(notes[1].text, " sample_text_2")
