import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from maidi import MidiScore, TagManager
from maidi.integrations.api import MusicLangAPI
from maidi import instrument

API_URL = "https://api.mockmusiclang.io"
MUSICLANG_API_KEY = "testapikey"


@pytest.fixture
def setup_api():
    return MusicLangAPI(api_url=API_URL, api_key=MUSICLANG_API_KEY, verbose=True)


@pytest.fixture
def setup_score():
    instruments = [instrument.PIANO]
    score = MidiScore.from_empty(instruments=instruments, nb_bars=8, ts=(4, 4), tempo=120)
    return score

@pytest.fixture
def setup_score_two_tracks():
    instruments = [instrument.PIANO, instrument.VIOLIN]
    score = MidiScore.from_empty(instruments=instruments, nb_bars=8, ts=(4, 4), tempo=120)
    return score


def test_determine_bars_step(setup_api):
    api = setup_api

    step = api._determine_bars_step(nb_added_bars_step=4, remaining_bars=10)
    assert step == 4

    step = api._determine_bars_step(nb_added_bars_step=None, remaining_bars=10)
    assert step == min(api.MAX_CONTEXT, 10)


def test_create_mask(setup_api, setup_score):
    api = setup_api
    score = setup_score
    score = score.add_silence_bars(8)
    mask = api._create_mask(score, 4)

    assert mask.shape == (score.nb_tracks, score.nb_bars)
    assert np.array_equal(mask[:, -4:], np.ones((score.nb_tracks, 4)))
    assert np.array_equal(mask[:, :-4], np.zeros((score.nb_tracks, score.nb_bars - 4)))



@patch.object(MusicLangAPI, 'predict')
def test_extend(mock_predict, setup_api, setup_score):
    api = setup_api
    score = setup_score

    def predict_side_effect(predicted_score, *args, **kwargs):
        return predicted_score  # Return the input segment as the result

    mock_predict.side_effect = predict_side_effect

    extended_score = api.extend(score, nb_bars_added=4, model="control_masking_large", nb_added_bars_step=None,
                                chords=None, tags=None, timeout=120, temperature=0.95, polling_interval=1)

    assert mock_predict.called
    assert extended_score is not None
    assert extended_score.nb_bars == score.nb_bars + 4

    # Testing with nb_added_bars_step
    extended_score = api.extend(score, nb_bars_added=8, model="control_masking_large", nb_added_bars_step=4,
                                chords=None, tags=None, timeout=120, temperature=0.95, polling_interval=1)

    assert mock_predict.called
    assert extended_score is not None
    assert extended_score.nb_bars == score.nb_bars + 8

@patch.object(MusicLangAPI, 'predict')
def test_extend_wrong_number_of_tags_track(mock_predict, setup_api, setup_score_two_tracks):
    api = setup_api
    score = setup_score_two_tracks

    def predict_side_effect(predicted_score, *args, **kwargs):
        return predicted_score

    mock_predict.side_effect = predict_side_effect
    mask, tags, chords = score.get_empty_controls()
    tags = TagManager(tags)
    tags_wrong = tags[1:, :4]  # NB BARS GOOD = 4, but wrong number of tracks

    with pytest.raises(ValueError) as e:
        api.extend(score, nb_bars_added=4, model="control_masking_large", nb_added_bars_step=None,
                                chords=None, tags=tags_wrong, timeout=120, temperature=0.95, polling_interval=1)

    assert "Wrong number of tracks in tags" in str(e.value)

@patch.object(MusicLangAPI, 'predict')
def test_extend_wrong_number_of_bars(mock_predict, setup_api, setup_score):
    api = setup_api
    score = setup_score

    def predict_side_effect(predicted_score, *args, **kwargs):
        return predicted_score

    mock_predict.side_effect = predict_side_effect
    mask, tags, chords = score.get_empty_controls()
    tags = TagManager(tags)
    tags_wrong = tags[:, :2]

    with pytest.raises(ValueError) as e:
        api.extend(score, nb_bars_added=4, model="control_masking_large", nb_added_bars_step=None,
                                chords=None, tags=tags_wrong, timeout=120, temperature=0.95, polling_interval=1)

    assert "Wrong number of bars in tags" in str(e.value)

@patch.object(MusicLangAPI, 'predict')
def test_extend_wrong_number_of_chords(mock_predict, setup_api, setup_score):
    api = setup_api
    score = setup_score

    mask, tags, chords = score.get_empty_controls()
    from maidi import ChordManager
    chords_wrong = ChordManager(chords[:2])

    with pytest.raises(ValueError) as e:
        api.extend(score, nb_bars_added=4, model="control_masking_large", nb_added_bars_step=None,
                                chords=chords_wrong, tags=None, timeout=120, temperature=0.95, polling_interval=1)

    assert "Wrong number of chords" in str(e.value)


if __name__ == "__main__":
    pytest.main()
