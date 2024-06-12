import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from maidi import MidiScore
from maidi.integrations.api import MusicLangAPI
from maidi import instrument

API_URL = "https://api.mockmusiclang.io"
API_KEY = "testapikey"

@pytest.fixture
def setup_api():
    return MusicLangAPI(api_url=API_URL, api_key=API_KEY, verbose=True)

@pytest.fixture
def setup_scores():
    instruments = [instrument.PIANO]
    score1 = MidiScore.from_empty(instruments=instruments, nb_bars=8, ts=(4, 4), tempo=120)
    score2 = MidiScore.from_empty(instruments=instruments, nb_bars=8, ts=(4, 4), tempo=120)
    return score1, score2

def test_validate_transition_params(setup_api, setup_scores):
    api = setup_api
    score1, score2 = setup_scores
    score1 = score1.copy()
    score2 = score2.copy()
    api._validate_transition_params(score1, score2, 4)

    score2_too_much_instruments = score2.add_instrument(instrument.CLEAN_GUITAR)
    with pytest.raises(ValueError) as excinfo:
        api._validate_transition_params(score1, score2_too_much_instruments, 4)
    assert "The number of tracks in score1 and score2 must be the same" in str(excinfo.value)

    score1_new_instrument = score1.change_instrument(0, instrument.ACOUSTIC_GUITAR)
    with pytest.warns(UserWarning, match="Instruments are different in the two scores"):
        api._validate_transition_params(score1_new_instrument, score2, 4)

    with pytest.raises(ValueError) as excinfo:
        api._validate_transition_params(score1, score2, 13)
    assert "Transition size must be less than" in str(excinfo.value)

def test_calculate_bars_to_take(setup_api, setup_scores):
    api = setup_api
    score1, score2 = setup_scores
    nb_bars_score1, nb_bars_score2 = api._calculate_bars_to_take(score1, score2, 4)
    assert nb_bars_score1 == 6
    assert nb_bars_score2 == 6

def test_create_transition_segment(setup_api, setup_scores):
    api = setup_api
    score1, score2 = setup_scores
    score1 = score1.copy()
    score2 = score2.copy()
    nb_bars_score1 = 6
    nb_bars_transition = 4
    nb_bars_score2 = 6
    segment = api._create_transition_segment(score1, score2, nb_bars_score1, nb_bars_transition, nb_bars_score2)
    assert segment.nb_bars == nb_bars_score1 + nb_bars_transition + nb_bars_score2

def test_create_transition_mask(setup_api, setup_scores):
    api = setup_api
    score1, score2 = setup_scores
    score1 = score1.copy()
    score2 = score2.copy()
    nb_bars_score1 = 6
    nb_bars_transition = 4
    segment = api._create_transition_segment(score1, score2, nb_bars_score1, nb_bars_transition, 6)
    mask = api._create_transition_mask(score1.nb_tracks, segment.nb_bars, nb_bars_score1, nb_bars_transition)
    assert np.array_equal(mask[:, nb_bars_score1:nb_bars_score1 + nb_bars_transition], np.ones((score1.nb_tracks, nb_bars_transition)))
    assert np.array_equal(mask[:, :nb_bars_score1], np.zeros((score1.nb_tracks, nb_bars_score1)))
    assert np.array_equal(mask[:, nb_bars_score1 + nb_bars_transition:], np.zeros((score1.nb_tracks, 6)))

@patch.object(MusicLangAPI, 'predict')
def test_create_transition(mock_predict, setup_api, setup_scores):
    api = setup_api
    score1, score2 = setup_scores
    score1 = score1.copy()
    score2 = score2.copy()

    def predict_side_effect(segment, mask, model, timeout, temperature, async_mode, polling_interval, chords, tags, **prediction_kwargs):
        return segment  # Return the input segment as the result

    mock_predict.side_effect = predict_side_effect

    result = api.create_transition(score1, score2, 4, return_all=True)
    assert mock_predict.called
    assert result is not None

    result = api.create_transition(score1, score2, 4, return_all=False)
    assert mock_predict.called
    assert result is not None