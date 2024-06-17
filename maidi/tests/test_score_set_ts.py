import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from maidi import MidiScore
from maidi import instrument
import os

@pytest.fixture
def setup_score():
    instruments = [instrument.PIANO]
    score = MidiScore.from_empty(instruments=instruments, nb_bars=8, ts=(4, 4), tempo=120)
    return score

def test_dilate_time_single_factor(setup_score):
    score = setup_score
    factor = 2.0
    original_times = [track["time"].copy() for track in score.tracks[score.track_keys[0]]]
    original_durations = [track["duration"].copy() for track in score.tracks[score.track_keys[0]]]

    dilated_score = score.dilate_time(factor)

    for bar in range(len(dilated_score.bars)):
        track = dilated_score.tracks[dilated_score.track_keys[0]][bar]
        assert np.array_equal(track["time"], (original_times[bar] * factor).astype(np.int32))
        assert np.array_equal(track["duration"], (original_durations[bar] * factor).astype(np.int32))

def test_dilate_time_multiple_factors(setup_score):
    score = setup_score
    factors = [1.0, 1.5, 2.0, 0.5, 1.0, 1.5, 2.0, 0.5]
    original_times = [track["time"].copy() for track in score.tracks[score.track_keys[0]]]
    original_durations = [track["duration"].copy() for track in score.tracks[score.track_keys[0]]]

    dilated_score = score.dilate_time(factors)

    for bar in range(len(dilated_score.bars)):
        track = dilated_score.tracks[dilated_score.track_keys[0]][bar]
        factor = factors[bar]
        assert np.array_equal(track["time"], (original_times[bar] * factor).astype(np.int32))
        assert np.array_equal(track["duration"], (original_durations[bar] * factor).astype(np.int32))

def test_change_ts_no_dilate(setup_score):
    from copy import deepcopy
    score = setup_score
    new_ts = (3, 8)
    original_bars = score.bars.copy()

    changed_score = score.change_ts(new_ts, dilate_time=False)

    for idx, bar in enumerate(changed_score.bars):
        assert bar[score.TIME_SIGNATURE_NUMERATOR_INDEX] == new_ts[0]
        assert bar[score.TIME_SIGNATURE_DENOMINATOR_INDEX] == new_ts[1]
        assert bar[score.TIME_SIGNATURE_NUMERATOR_INDEX] != original_bars[idx][score.TIME_SIGNATURE_NUMERATOR_INDEX]
        assert bar[score.TIME_SIGNATURE_DENOMINATOR_INDEX] != original_bars[idx][score.TIME_SIGNATURE_DENOMINATOR_INDEX]

def test_change_ts_with_dilate(setup_score):
    score = setup_score
    new_ts = (3, 4)
    original_times = [track["time"].copy() for track in score.tracks[score.track_keys[0]]]
    original_durations = [track["duration"].copy() for track in score.tracks[score.track_keys[0]]]

    changed_score = score.change_ts(new_ts, dilate_time=True)

    for idx, bar in enumerate(changed_score.bars):
        assert bar[score.TIME_SIGNATURE_NUMERATOR_INDEX] == new_ts[0]
        assert bar[score.TIME_SIGNATURE_DENOMINATOR_INDEX] == new_ts[1]

    dilate_factors = []
    for idx_bar, bar in enumerate(score.bars):
        original_bar_duration = score._get_bar_duration_from_bar(bar, score.tpq)
        new_bar = list(bar)
        new_bar[score.TIME_SIGNATURE_NUMERATOR_INDEX] = new_ts[0]
        new_bar[score.TIME_SIGNATURE_DENOMINATOR_INDEX] = new_ts[1]
        new_bar_duration = score._get_bar_duration_from_bar(new_bar, score.tpq)
        dilate_factors.append(new_bar_duration / original_bar_duration)

    for bar in range(len(changed_score.bars)):
        track = changed_score.tracks[changed_score.track_keys[0]][bar]
        factor = dilate_factors[bar]
        assert np.array_equal(track["time"], (original_times[bar] * factor).astype(np.int32))
        assert np.array_equal(track["duration"], (original_durations[bar] * factor).astype(np.int32))