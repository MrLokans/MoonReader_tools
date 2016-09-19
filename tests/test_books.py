import unittest

from moonreader_tools.books import Book, BookTypeError, ParamTypeError


class TestBooks(unittest.TestCase):

    def test_book_type_correctly_parsed_from_simple_name(self):
        simple_name = "/test/book.pdf.po"
        self.assertEqual(Book._get_book_type(simple_name), "pdf")

    def test_book_type_correctly_parsed_from_name_with_double_zip_ext(self):
        simple_name = "/test/book.fb2.zip.po"
        self.assertEqual(Book._get_book_type(simple_name), "fb2")

    def test_book_type_correctly_get_from_zip_ext(self):
        simple_name = "/test/book.zip.po"
        self.assertEqual(Book._get_book_type(simple_name), "zip")

    def test_exception_raised_when_type_is_not_correct(self):
        simple_name = "/test/book.djvu"
        with self.assertRaises(BookTypeError):
            Book._get_book_type(simple_name, allowed_types=("fb2", "pdf"))

    def test_exception_raised_when_parsing_noextname(self):
        simple_name = "/test/book_with_no_extension"
        with self.assertRaises(BookTypeError):
            Book._get_book_type(simple_name, allowed_types=("fb2", "pdf"))

    def test_incorrect_extension_parsing_raises_error(self):
        filename = "/test/book.ext"
        with self.assertRaises(BookTypeError):
            Book._get_book_type(filename, extensions=(".po", ".an"))

    def test_default_type_returned_when_parsing_generic_file(self):
        simple_name = "/test/tricky_book"
        book_type = Book._get_book_type(simple_name, default_type="pdf")
        self.assertEqual(book_type, "pdf")

    def test_incorrect_name_with_dot_in_path_raises_error(self):
        filename = "/test/.tricky_dir/filename.po"
        with self.assertRaises(BookTypeError):
            Book._get_book_type(filename)

    def test_attempting_to_save_book_with_path_and_stats_param_raises_error(self):
        book = Book("test", None, None)
        with self.assertRaises(ParamTypeError):
            book.save(path="test", stats_file="test.po")

    def test_attempting_to_save_book_with_path_and_notes_param_raises_error(self):
        book = Book("test", None, None)
        with self.assertRaises(ParamTypeError):
            book.save(path="test", notes_file="test.an")

    def test_attempting_to_save_book_with_all_paths_params_raises_error(self):
        book = Book("test", None, None)
        with self.assertRaises(ParamTypeError):
            book.save(path="test", notes_file="test.an", stats_file="test.po")


def test_book_object_stat_is_constructed_from_dict():
    book = Book('title', stats={'percentage': 20, 'pages': 10})

    assert book.title == 'title'
    assert book.percentage == 20
    assert book.pages == 10


if __name__ == '__main__':
    unittest.main()
