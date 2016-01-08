import os
import json

from .stat import MoonReaderStatistics
from .parsers import MoonReaderNotes


class MoonReaderBookData(object):

    def __init__(self, title, stats, notes):
        self.title = title
        self.stats = stats
        self.notes = notes

    def to_dict(self):
        return {
            'title': self.title,
            'pages': self.stats.pages,
            'percentage': self.stats.percentage,
            'notes': [note.to_dict() for note in self.notes]
        }

    def to_json(self):
        # print(self.to_dict())
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @staticmethod
    def _from_file_tuple(tpl):
        stat_file, note_file = tpl
        fname = stat_file if stat_file else note_file
        title = MoonReaderBookData._title_from_fname(fname)
        return MoonReaderBookData(title,
                                  MoonReaderStatistics.from_file(note_file),
                                  MoonReaderNotes.from_file(stat_file).notes)

    @classmethod
    def _title_from_fname(cls, fname):
        fname = os.path.split(fname)[-1]
        if fname.endswith((".po", ".an")):
            fname = fname[:-3]
        if fname.endswith(".fb2.zip"):
            fname = fname[:-8]
        if fname.endswith((".fb2", ".pdf")):
            fname = fname[:-4]
        if fname.endswith(".epub"):
            fname = fname[:-5]
        print(fname)
        return fname

    def __str__(self):
        return "<Book> {}: {} notes".format(self.title, len(self.notes))

    def __repr__(self):
        return self.__str__()
