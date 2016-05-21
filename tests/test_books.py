import unittest

from moonreader_tools.books import Book


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
        with self.assertRaises(ValueError):
            Book._get_book_type(simple_name, allowed_types=("fb2", "pdf"))

    def test_exception_raised_when_parsing_noextname(self):
        simple_name = "/test/book_with_no_extension"
        with self.assertRaises(ValueError):
            Book._get_book_type(simple_name, allowed_types=("fb2", "pdf"))

    def test_default_type_returned_when_parsing_generic_file(self):
        simple_name = "/test/tricky_book"
        book_type = Book._get_book_type(simple_name, default_type="pdf")
        self.assertEqual(book_type, "pdf")

if __name__ == '__main__':
    unittest.main()
