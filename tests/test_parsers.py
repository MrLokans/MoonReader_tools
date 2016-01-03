import unittest
from moonreader_tools.parsers import PDF_Note_Parser, FB2_Note_Parser
from moonreader_tools.stat import MoonReaderStatistics

from moonreader_tools.notes import AbstractNote

from .base import BaseTest


class TestPDFParserRoutines(BaseTest):

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


class TestFB2ParserRoutines(BaseTest):

    def test_note_text_correctly_splitted_into_header_and_rest(self):
        header = self.generate_note_header()
        note_text = self.generate_note_text()
        note_content = header + note_text
        splitted_header, splitted_note_text = FB2_Note_Parser.split_note_text(note_content.splitlines())
        self.assertEqual(header.splitlines(), splitted_header)
        self.assertEqual(note_text.splitlines(), splitted_note_text)

    def test_reads_raw_text_correctly(self):
        parser = FB2_Note_Parser.from_text(self.sample_note_text)

        self.assertEqual(len(parser.notes), 2)
        note_1 = parser.notes[0]

        self.assertEqual(note_1.text, "Some text")
        self.assertEqual(note_1.id, '2984')
        self.assertEqual(note_1.modifier, AbstractNote.MARKER)


class TestStatistics(unittest.TestCase):

    def test_full_str_is_parsed_correctly(self):
        test_str = "1392540515970*15@0#6095:7.8%"
        po = MoonReaderStatistics.from_string(test_str)
        self.assertEqual(po.percentage, 7.8)
        self.assertEqual(po.pages, 15)
        self.assertEqual(po.uid, "1392540515970")