import os
import shutil
import tempfile

import pytest

from moonreader_tools.parsers.base import BookParser

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURE_DIR = os.path.join(BASE_DIR, "book_fixtures")


@pytest.yield_fixture(scope="session")
def temp_dir():
    temp_dir = tempfile.mkdtemp(prefix="book_dir")

    yield temp_dir
    shutil.rmtree(temp_dir)


fixture_valid_pdf_notes_path = os.path.join(FIXTURE_DIR, "How_Linux_Works.pdf.an")
fixture_valid_pdf_stats_path = os.path.join(FIXTURE_DIR, "How_Linux_Works.pdf.po")

fixture_valid_fb2_notes_path = os.path.join(FIXTURE_DIR, "Do_Smerti_Zdorov.fb2.an")
fixture_valid_fb2_stats_path = os.path.join(FIXTURE_DIR, "Do_Smerti_Zdorov.fb2.po")

fixture_valid_fb2_with_manual_note_notes_path = os.path.join(
    FIXTURE_DIR, "Brinkman_S._Konec_Yepohi_Self_Help_Ka.fb2.zip.an"
)
fixture_valid_fb2_with_manual_note_stats_path = os.path.join(
    FIXTURE_DIR, "Brinkman_S._Konec_Yepohi_Self_Help_Ka.fb2.zip.po"
)


def test_reading_valid_pdf_book_with_stats_and_notes():
    with BookParser.from_files(
        fixture_valid_pdf_notes_path, fixture_valid_pdf_stats_path
    ) as reader:
        book = reader.build()

        assert int(book.percentage) == 44
        assert book.pages == 151
        assert book.title == "How_Linux_Works"
        assert len(book.notes) == 79
        assert book.notes[-1].text == "need"


def test_reading_valid_fb2_book_with_stats_and_notes():
    with BookParser.from_files(
        fixture_valid_fb2_notes_path, fixture_valid_fb2_stats_path
    ) as reader:
        book = reader.build()
        assert int(book.percentage) == 100
        assert book.pages == 155
        assert book.title == "Do_Smerti_Zdorov"
        assert len(book.notes) == 20
        assert book.notes[0].text[:30] == "Наверное, нужно было сказать п"
        assert book.notes[-1].text[:30] == "Поэтому Уонсик советует «делат"


def test_reading_valid_fb2_book_with_bookmark_and_manual_note():
    with BookParser.from_files(
        fixture_valid_fb2_with_manual_note_notes_path,
        fixture_valid_fb2_with_manual_note_stats_path,
    ) as reader:
        book = reader.build()
        assert len(book.notes) > 2
        book_note_with_mark = book.notes[2]

        assert book_note_with_mark.note[:30] == "автор пытается сказать или нам"
