"""
Representation of the moon reader's statistics object.
"""
import time


class Statistics(object):
    def __init__(self, timestamp=None, pages=0, percentage=0, **kwargs):
        if timestamp is None:
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        self.pages = int(pages)
        self.percentage = float(percentage)
        self._rest = kwargs

    def __repr__(self) -> str:
        return (
            "Statistics("
            "percentage={0},"
            "pages={1})".format(self.percentage, self.pages)
        )

    def __str__(self) -> str:
        return self.__repr__()

    def to_dict(self):
        return {"percentage": self.percentage, "pages": self.pages}

    @classmethod
    def empty_stats(cls):
        """Returns empty statistics object."""
        return cls(pages=0, percentage=0)

    def is_empty(self):
        return all([self.pages == 0, self.percentage == 0])
