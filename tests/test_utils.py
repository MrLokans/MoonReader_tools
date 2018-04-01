import os
import unittest

from moonreader_tools.errors import BookTypeError

from unittest.mock import patch

from moonreader_tools.utils import (
    get_moonreader_files,
    one_obj_or_list,
    get_same_book_files,
    get_book_type)


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


class TestBookType(unittest.TestCase):

    def test_book_type_correctly_parsed_from_simple_name(self):
        simple_name = "/test/book.pdf.po"
        self.assertEqual(get_book_type(simple_name), "pdf")

    def test_book_type_correctly_parsed_from_name_with_double_zip_ext(self):
        simple_name = "/test/book.fb2.zip.po"
        self.assertEqual(get_book_type(simple_name), "fb2")

    def test_book_type_correctly_get_from_zip_ext(self):
        simple_name = "/test/book.zip.po"
        self.assertEqual(get_book_type(simple_name), "zip")

    def test_exception_raised_when_type_is_not_correct(self):
        simple_name = "/test/book.djvu"
        with self.assertRaises(BookTypeError):
            get_book_type(simple_name, allowed_types=("fb2", "pdf"))

    def test_exception_raised_when_parsing_noextname(self):
        simple_name = "/test/book_with_no_extension"
        with self.assertRaises(BookTypeError):
            get_book_type(simple_name, allowed_types=("fb2", "pdf"))

    def test_incorrect_extension_parsing_raises_error(self):
        filename = "/test/book.ext"
        with self.assertRaises(BookTypeError):
            get_book_type(filename, extensions=(".po", ".an"))

    def test_default_type_returned_when_parsing_generic_file(self):
        simple_name = "/test/tricky_book"
        book_type = get_book_type(simple_name, default_type="pdf")
        self.assertEqual(book_type, "pdf")

    def test_incorrect_name_with_dot_in_path_raises_error(self):
        filename = "/test/.tricky_dir/filename.po"
        with self.assertRaises(BookTypeError):
            get_book_type(filename)


if __name__ == '__main__':
    unittest.main()
