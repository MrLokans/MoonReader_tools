import unittest

from tests.test_utils import (
    TestFileRoutines,
    TestColorExtractingRoutines,
    TestHelperMethods
)
from tests.test_parsers import (
    TestPDFParserRoutines, TestFB2ParserRoutines,
    TestStatisticsParser, TestMoonReaderNotes,
    TestGenericParsers
)
from tests.test_notes import TestPDFNotes, TestFB2Notes
from tests.test_books import TestBooks

if __name__ == '__main__':

    loader = unittest.TestLoader()
    suite = unittest.TestSuite((
        loader.loadTestsFromTestCase(TestFileRoutines),
        loader.loadTestsFromTestCase(TestHelperMethods),
        loader.loadTestsFromTestCase(TestColorExtractingRoutines),

        loader.loadTestsFromTestCase(TestPDFParserRoutines),
        loader.loadTestsFromTestCase(TestFB2ParserRoutines),
        loader.loadTestsFromTestCase(TestGenericParsers),
        loader.loadTestsFromTestCase(TestStatisticsParser),
        loader.loadTestsFromTestCase(TestMoonReaderNotes),

        loader.loadTestsFromTestCase(TestPDFNotes),
        loader.loadTestsFromTestCase(TestFB2Notes),

        loader.loadTestsFromTestCase(TestBooks),

    ))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
