
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from maidi import MidiScore
from maidi.integrations.api import MusicLangAPI
from maidi import instrument
import os




@pytest.fixture
def setup_score():
    instruments = [instrument.PIANO]
    score = MidiScore.from_empty(instruments=instruments, nb_bars=8, ts=(4, 4), tempo=120)
    return score

MUSICLANG_API_KEY = "testapikey"


@pytest.fixture
def setup_api():
    return MusicLangAPI(api_key=MUSICLANG_API_KEY, verbose=True)

def test_init_api_with_env(setup_score):
    # Set API key in environment variable
    os.environ['MUSICLANG_API_KEY'] = MUSICLANG_API_KEY

    api = MusicLangAPI()

    os.environ.pop('MUSICLANG_API_KEY')
    with pytest.raises(ValueError) as e:
        api = MusicLangAPI()
    assert "API key missing" in str(e.value)


def test_get_subchords_and_subtags(setup_api):
    api = setup_api

    chords = [(0, 4, 'm', ''), (0, 4, 'm', ''), (1, 4, 'm', ''), (1, 4, 'm', '')]
    tags = [[[], [], [], []]]  # 1 track, 4 bars
    subchords, subtags = api._get_subchords_and_subtags(chords, tags, 1, 3, 1)
    assert subchords == [None, (0, 4, 'm', ''), (1, 4, 'm', '')]
    assert subtags == [[[], [], []]]



def test_check_tags_exists(setup_api):

    api = setup_api
    tags = [[['FAKE TAG']]]

    with pytest.raises(ValueError) as e:
        api._check_tags_exists(tags)
    assert "Unexisting tags have been used : {'FAKE TAG'}" in str(e.value)



def test_check_chord_exists_ok(setup_api):
    api = setup_api
    chords = [(0, 4, 'm', '6(sus4)')]

    api._check_chords_exists(chords)


def test_check_chord_exists_wrong_mode(setup_api):
    api = setup_api
    chords = [(0, 4, 'lydian', '')]

    with pytest.raises(ValueError) as e:
        api._check_chords_exists(chords)
    assert "Scale mode is wrong" in str(e.value)



def test_check_chord_degree_wrong(setup_api):
    api = setup_api
    chords = [(-1, 4, 'm', '')]

    with pytest.raises(ValueError) as e:
        api._check_chords_exists(chords)
    assert "Chord degree is wrong" in str(e.value)

def test_check_tonality_degree_wrong(setup_api):
    api = setup_api
    chords = [(0, -1, 'm', '')]

    with pytest.raises(ValueError) as e:
        api._check_chords_exists(chords)
    assert "Tonality degree is wrong" in str(e.value)

def test_check_extension_wrong(setup_api):
    api = setup_api
    chords = [(0, 0, 'm', 'wrong')]

    with pytest.raises(ValueError) as e:
        api._check_chords_exists(chords)
    assert "Wrong extension" in str(e.value)


@patch.object(MusicLangAPI, '_call_polling_api')
def test_poll_api_raise_error_when_failed(mock_call_polling_api, setup_api):

    def side_effect(*args, **kwargs):
        return {"status": "FAILED"}

    mock_call_polling_api.side_effect = side_effect

    api = setup_api
    with pytest.raises(RuntimeError) as e:
        api.poll_api("test_id")
    assert "Task failed" in str(e.value)


@patch.object(MusicLangAPI, '_call_polling_api')
def test_poll_api_returns_none_when_pending(mock_call_polling_api, setup_api):

    def side_effect(*args, **kwargs):
        return {"status": "PENDING"}

    mock_call_polling_api.side_effect = side_effect

    api = setup_api
    result = api.poll_api("test_id")
    assert result is None