import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from maidi import MidiScore
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


def test_determine_bars_step(setup_api):
    api = setup_api

    step = api._determine_bars_step(nb_added_bars_step=4, remaining_bars=10)
    assert step == 4

    step = api._determine_bars_step(nb_added_bars_step=None, remaining_bars=10)
    assert step == min(api.MAX_CONTEXT, 10)



@patch.object(MusicLangAPI, 'predict')
def test_generate_from_scratch(mock_predict, setup_api, setup_score):
    api = setup_api
    score = setup_score

    def predict_side_effect(predicted_score, mask, model, tags, chords, temperature, polling_interval, timeout,
                            **prediction_kwargs):
        return predicted_score  # Return the input segment as the result

    mock_predict.side_effect = predict_side_effect

    generated_score = api.generate_from_scratch(instruments=["piano"], nb_bars=8, ts=(4, 4), tempo=120, temperature=0.95,
                                               model="control_masking_large", timeout=120, polling_interval=1)

    assert mock_predict.called
    assert generated_score is not None
    assert generated_score.nb_bars == 8



if __name__ == "__main__":
    pytest.main()
