"""
Module, containing classes used to parse book data from files and string
"""
from typing import List

from moonreader_tools.stat import Statistics
from moonreader_tools.notes import Note


class Book(object):
    """
    Simple DTO representing a book in the system,
    with its statistics and attached notes if any
    """

    def __init__(self, title, stats=None, notes: List[Note] = None) -> None:
        """
        :param title: Book title
        :param stats: Statistics object
        :param notes: list of Note objects
        """
        self.title = title
        self.stats = stats
        self.stats = stats or Statistics.empty_stats()
        self.notes = notes or []

    @property
    def pages(self):
        return self.stats.pages

    @pages.setter
    def pages(self, value):
        self.stats.pages = value

    @property
    def stats(self):
        return self.__stats

    @stats.setter
    def stats(self, stats_obj):
        self.__stats = stats_obj

    @property
    def percentage(self):
        return self.stats.percentage

    @percentage.setter
    def percentage(self, value):
        self.stats.percentage = value

    def to_dict(self):
        """Serialize book to dictionary"""
        book_dict = {
            "title": self.title,
            "pages": self.pages,
            "percentage": self.percentage,
            "notes": [note.to_dict() for note in self.notes],
        }
        return book_dict

    def __str__(self):
        return "<Book> {}: {} notes".format(self.title, len(self.notes))

    def __repr__(self):
        return str(self)
