import unittest

from .test_utils import TestFileRoutines, TestColorExtractingRoutines, TestHelperMethods
from .test_parsers import TestPDFParserRoutines, TestFB2ParserRoutines, TestStatistics, TestMoonReaderNotes
from .test_notes import TestPDFNotes, TestFB2Notes

if __name__ == '__main__':

    loader = unittest.TestLoader()
    suite = unittest.TestSuite((
        loader.loadTestsFromTestCase(TestFileRoutines),
        loader.loadTestsFromTestCase(TestHelperMethods),
        loader.loadTestsFromTestCase(TestColorExtractingRoutines),

        loader.loadTestsFromTestCase(TestPDFParserRoutines),
        loader.loadTestsFromTestCase(TestFB2ParserRoutines),
        loader.loadTestsFromTestCase(TestStatistics),
        loader.loadTestsFromTestCase(TestMoonReaderNotes),

        loader.loadTestsFromTestCase(TestPDFNotes),
        loader.loadTestsFromTestCase(TestFB2Notes),

        ))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
