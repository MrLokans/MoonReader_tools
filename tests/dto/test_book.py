from moonreader_tools.books import Book


def test_book_is_properly_constructed_with_defaults():
    test_book_title = "My cool book"
    book = Book(test_book_title)

    assert book.title == test_book_title
    assert book.notes == []
    assert book.stats.pages == book.pages == 0
    assert book.stats.percentage == book.percentage == 0


def test_book_is_properly_serialized_into_dict():
    pass
