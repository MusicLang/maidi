import pytest
import numpy as np
from unittest.mock import patch
from maidi import MidiScore
from maidi.integrations.api import MusicLangAPI

API_URL = "https://api.mockmusiclang.io"
API_KEY = "testapikey"

@pytest.fixture
def setup_api():
    return MusicLangAPI(api_url=API_URL, api_key=API_KEY, verbose=True)

@pytest.fixture
def setup_score():
    instruments = ['piano']
    return MidiScore.from_empty(instruments=instruments, nb_bars=4, ts=(4, 4), tempo=120)

def test_initialization(setup_api):
    api = setup_api
    assert api.api_url == API_URL
    assert api.api_key == API_KEY
    assert api.verbose is True

def test_invalid_model(setup_api, setup_score):
    api = setup_api
    score = setup_score
    mask = np.ones((1, 4))
    with pytest.raises(ValueError) as excinfo:
        api.predict(score, mask, model="invalid_model")
    assert "Model invalid_model not existing" in str(excinfo.value)

def test_invalid_temperature(setup_api, setup_score):
    api = setup_api
    score = setup_score
    mask = np.ones((1, 4))
    with pytest.raises(ValueError) as excinfo:
        api.predict(score, mask, temperature=1.5)
    assert "Temperature must be lower than 1.0" in str(excinfo.value)

def test_invalid_mask_dimension(setup_api, setup_score):
    api = setup_api
    score = setup_score
    mask = np.ones((2, 4))  # Invalid mask shape
    with pytest.raises(ValueError) as excinfo:
        api.predict(score, mask)
    assert "Wrong number of tracks in the mask" in str(excinfo.value)

    mask = np.ones((1, 5))  # Invalid mask shape
    with pytest.raises(ValueError) as excinfo:
        api.predict(score, mask)
    assert "Wrong number of bars in the mask" in str(excinfo.value)

    mask = np.zeros((1, 4))  # Mask should not have only 0
    with pytest.raises(ValueError) as excinfo:
        api.predict(score, mask)
    assert "Mask must have at least one 1" in str(excinfo.value)

def test_invalid_chords(setup_api, setup_score):
    api = setup_api
    score = setup_score
    mask = np.ones((1, 4))
    invalid_chords = [(8, 0, 'M', '')]  # Invalid chord degree
    with pytest.raises(ValueError) as excinfo:
        api.predict(score, mask, chords=invalid_chords)
    assert "Chord degree is wrong" in str(excinfo.value)

@patch.object(MusicLangAPI, '_predict_with_api')
def test_predict_call(mock_predict_with_api, setup_api, setup_score):
    api = setup_api
    score = setup_score
    mask = np.ones((1, 4))
    api.predict(score, mask, model="control_masking_large")
    assert mock_predict_with_api.called

@patch.object(MusicLangAPI, '_predict_with_api')
def test_predict_with_tags(mock_predict_with_api, setup_api, setup_score):
    api = setup_api
    score = setup_score
    mask = np.ones((1, 4))
    tags = [[['CONTROL_MIN_POLYPHONY__1'] for _ in range(4)] for _ in range(1)]
    api.predict(score, mask, tags=tags)
    assert mock_predict_with_api.called

@patch.object(MusicLangAPI, '_predict_with_api')
def test_predict_with_chords(mock_predict_with_api, setup_api, setup_score):
    api = setup_api
    score = setup_score
    mask = np.ones((1, 4))
    chords = [(0, 0, 'M', '') for _ in range(4)]
    api.predict(score, mask, chords=chords)
    assert mock_predict_with_api.called
