import os
import unittest
from unittest.mock import patch

from moonreader_tools.utils import (date_from_long_timestamp, get_moonreader_files, one_obj_or_list,
                                    rgb_string_from_hex, rgba_hex_from_int, get_same_book_files)


class TestHelperMethods(unittest.TestCase):

    def test_one_or_list_returns_list_for_list_of_many_objects(self):
        l = [1, 2]
        self.assertEqual(one_obj_or_list(l), [1, 2])

    def test_one_or_list_returns_one_object_for_list_of_single_object(self):
        l = [100]
        self.assertEqual(one_obj_or_list(l), 100)


class TestFileRoutines(unittest.TestCase):

    @patch('moonreader_tools.utils.os.listdir')
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


if __name__ == '__main__':
    unittest.main()
