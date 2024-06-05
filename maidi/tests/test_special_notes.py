import pytest
from unittest.mock import patch
from maidi.analysis.control_features.special_notes import _get_special_notes_tags

# Define some constants for test cases
TRACK_BAR_1 = {
    "pitch": [60, 62, 64, 65],
    "velocity": [90, 85, 80, 75],
    "time": [0, 1, 2, 3],
    "duration": [1, 1, 1, 1],
}

TRACK_BAR_2 = {
    "pitch": [60, 61, 62, 63],
    "velocity": [90, 85, 80, 75],
    "time": [0, 1, 2, 3],
    "duration": [2, 2, 1, 1],
}

TRACK_BAR_3 = {
    "pitch": [60, 61, 62, 63, 64, 65],
    "velocity": [90, 85, 80, 75, 70, 65],
    "time": [0, 1, 2, 3, 4, 5],
    "duration": [1, 1, 1, 1, 1, 1],
}

CHORD = "Cmaj7"


@pytest.fixture
def mock_parse_pitch():
    """ """
    with patch("maidi.analysis.control_features.special_notes.parse_pitch") as mock:
        yield mock


def test_get_special_notes_tags_case_1(mock_parse_pitch):
    """

    Parameters
    ----------
    mock_parse_pitch :
        

    Returns
    -------

    """
    # Mocking parse_pitch to return some interesting and some uninteresting values
    mock_parse_pitch.side_effect = [
        ("s", 1, 4),  # Ninth in the scale (interesting)
        ("s", 3, 4),  # Fourth (interesting)
        ("s", 0, 4),  # Not interesting
        ("s", 0, 4),  # Not interesting
    ]

    result = _get_special_notes_tags(TRACK_BAR_1, CHORD)
    assert result == [("s", 1), ("s", 3)]


def test_get_special_notes_tags_case_2(mock_parse_pitch):
    """

    Parameters
    ----------
    mock_parse_pitch :
        

    Returns
    -------

    """
    mock_parse_pitch.side_effect = [
        ("s", 1, 4),  # Ninth in the scale (interesting)
        ("h", 1, 4),  # b9 (interesting)
        ("h", 2, 4),  # 9 (chromatic) (interesting)
        ("s", 0, 4),  # Not interesting
    ]

    result = _get_special_notes_tags(TRACK_BAR_2, CHORD)
    assert result == [("s", 1), ("h", 1), ("h", 2)]


def test_get_special_notes_tags_case_3(mock_parse_pitch):
    """

    Parameters
    ----------
    mock_parse_pitch :
        

    Returns
    -------

    """
    mock_parse_pitch.side_effect = [
        ("s", 1, 4),  # Ninth in the scale (interesting)
        ("s", 3, 4),  # Fourth (interesting)
        ("s", 0, 4),  # Not interesting
        ("s", 0, 4),  # Not interesting
        ("s", 5, 4),  # Sixth (interesting)
        ("s", 0, 4),  # Not interesting
    ]

    result = _get_special_notes_tags(TRACK_BAR_3, CHORD)
    assert result == [
        ("s", 1),
        ("s", 3),
    ]  # Top 3 should be returned, but s0 in top 3 so not returned


def test_get_special_notes_tags_case_with_normalization(mock_parse_pitch):
    """

    Parameters
    ----------
    mock_parse_pitch :
        

    Returns
    -------

    """
    mock_parse_pitch.side_effect = [
        ("s", 1, 4),  # Ninth in the scale (interesting)
        ("s", 0, 4),  # Not interesting
        ("h", 2, 4),  # 9 (chromatic) (interesting)
        ("s", 1, 4),  # Ninth in the scale (interesting)
    ]

    track_bar = {
        "pitch": [60, 61, 62, 60],
        "velocity": [90, 85, 80, 75],
        "time": [0, 1, 2, 3],
        "duration": [2, 2, 2, 4],  # The last note has the longest duration
    }

    result = _get_special_notes_tags(track_bar, CHORD)
    assert result == [("s", 1), ("h", 2)]


def test_get_special_notes_tags_case_empty_bar(mock_parse_pitch):
    """

    Parameters
    ----------
    mock_parse_pitch :
        

    Returns
    -------

    """
    mock_parse_pitch.side_effect = []

    track_bar = {"pitch": [], "velocity": [], "time": [], "duration": []}

    result = _get_special_notes_tags(track_bar, CHORD)
    assert result == []


if __name__ == "__main__":
    pytest.main()
