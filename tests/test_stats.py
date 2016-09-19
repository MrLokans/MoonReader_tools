import sys
import unittest

try:
    from unittest.mock import patch, mock_open
except ImportError:
    from mock import patch, mock_open


from moonreader_tools.stat import Statistics
from moonreader_tools.conf import STAT_EXTENSION


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
    @patch('io.open')
    def test_empty_stats_return_for_empty_file_p2(self,
                                                  open_mock, path_exists_mock):
        open_mock.read.return_value = ""
        path_exists_mock.return_value = True
        s = Statistics.from_file("aa" + STAT_EXTENSION)
        self.assertTrue(s.is_empty())

    @patch('os.path.exists')
    @patch('io.open', mock_open(), create=True)
    def text_correctly_reads_from_file_p3(self, exists_mock, open_mock):
        open_mock.read.return_value = self.test_str
        exists_mock.return_value = True
        s = Statistics.from_file("aa" + STAT_EXTENSION)
        self.assertEqual(s.percentage, 7.8)
        self.assertEqual(s.pages, 15)
        self.assertEqual(s.uid, "1392540515970")
