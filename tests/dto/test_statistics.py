import pytest

from moonreader_tools.stat import Statistics


NON_ZERO_VALUE = 2


def test_statistics_default_values():
    stats = Statistics()

    assert isinstance(stats.timestamp, int)
    assert stats.pages == 0
    assert stats.percentage == 0


def test_is_empty_returns_true_for_zero_values():
    stats = Statistics(0, 0, 0)
    assert stats.is_empty() is True


def test_empty_stats_builds_empty_stats():
    empty_stats = Statistics.empty_stats()

    assert empty_stats.pages == 0
    assert empty_stats.percentage == 0


@pytest.mark.parametrize(
    "input_combinations",
    [
        (0, 0, NON_ZERO_VALUE),
        (0, NON_ZERO_VALUE, 0),
        (0, NON_ZERO_VALUE, NON_ZERO_VALUE),
    ],
)
def test_is_empty_returns_true_for_non_zero_values(input_combinations):

    stats = Statistics(*input_combinations)
    assert stats.is_empty() is False
