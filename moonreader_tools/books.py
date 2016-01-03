from .stat import MoonReaderStatistics
from .notes import MoonReaderNotes


class MoonReaderBookData(object):

    def __init__(self, stats, notes):
        self.stats = stats
        self.notes = notes

    def to_json(self):
        return {}

    @staticmethod
    def _from_file_tuple(tpl):
        stat_file, note_file = tpl
        return MoonReaderBookData(MoonReaderStatistics.from_file(note_file),
                                  MoonReaderNotes.from_file(stat_file))
