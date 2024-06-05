from maidi.analysis.control_features.polyphony import (
    get_min_polyphony,
    get_max_polyphony,
)  # Assume your functions are in 'your_module'


def test_get_max_polyphony_empty():
    """ """
    assert get_max_polyphony([]) == 0, "Max polyphony of empty list should be 0"


def test_get_min_polyphony_empty():
    """ """
    assert get_min_polyphony([]) == 0, "Min polyphony of empty list should be 0"


def test_get_max_polyphony_no_overlap():
    """ """
    notes = [(1, 2), (3, 4), (5, 6)]
    assert (
        get_max_polyphony(notes) == 1
    ), "Max polyphony with no overlapping notes should be 1"


def test_get_min_polyphony_no_overlap():
    """ """
    notes = [(1, 2), (3, 4), (5, 6)]
    assert (
        get_min_polyphony(notes) == 1
    ), "Min polyphony with no overlapping notes should be 1"


def test_get_max_polyphony_full_overlap():
    """ """
    notes = [(1, 3), (1, 3), (1, 3)]
    assert (
        get_max_polyphony(notes) == 3
    ), "Max polyphony with fully overlapping notes should be 3"


def test_get_min_polyphony_full_overlap():
    """ """
    notes = [(1, 3), (1, 3), (1, 3)]
    assert (
        get_min_polyphony(notes) == 3
    ), "Min polyphony with fully overlapping notes should be 3"


def test_get_min_polyphony_full_overlap_2():
    """ """
    notes = [(1, 3), (1, 3), (1, 3), (4, 5), (4, 5)]
    assert (
        get_min_polyphony(notes) == 2
    ), "Min polyphony with fully overlapping notes should be 2"


def test_get_max_polyphony_partial_overlap():
    """ """
    notes = [(1, 4), (2, 5), (3, 6)]
    assert (
        get_max_polyphony(notes) == 3
    ), "Max polyphony with partial overlaps should be 3"


def test_get_min_polyphony_partial_overlap():
    """ """
    notes = [(1, 4), (2, 5), (3, 6)]
    assert (
        get_min_polyphony(notes) == 1
    ), "Min polyphony with partial overlaps should be 1 when first note starts"


def test_get_max_polyphony_same_time_start_end():
    """ """
    notes = [(1, 5), (2, 2), (3, 6)]
    assert (
        get_max_polyphony(notes) == 2
    ), "Max polyphony should handle notes that start and end at the same time"


def test_get_min_polyphony_same_time_start_end():
    """ """
    notes = [(1, 5), (2, 2), (3, 6)]
    assert (
        get_min_polyphony(notes) == 1
    ), "Min polyphony should handle notes that start and end at the same time"


def test_get_max_polyphony_complex():
    """ """
    notes = [(1, 5), (2, 3), (4, 7), (6, 8)]
    assert (
        get_max_polyphony(notes) == 2
    ), "Max polyphony should correctly handle complex overlapping"


def test_get_min_polyphony_complex():
    """ """
    notes = [(1, 5), (2, 3), (4, 7), (6, 8)]
    assert (
        get_min_polyphony(notes) == 1
    ), "Min polyphony should correctly handle complex overlapping"


def test_get_max_polyphony_starts_when_other_ends():
    """ """
    notes = [(0, 1), (1, 2)]
    assert (
        get_max_polyphony(notes) == 1
    ), "Max polyphony should handle notes that start when another ends"


def test_min_polyphony_not_zero():
    """ """
    notes = [(0, 1), (2, 3), (4, 5)]
    assert (
        get_min_polyphony(notes) == 1
    ), "Min polyphony should not be zero when silence between two notes"
