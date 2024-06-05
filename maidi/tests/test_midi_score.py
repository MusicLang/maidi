from maidi import MidiScore, INSTRUMENTS_DICT
from maidi import instrument

import pytest
import tempfile

def create_fake_midi_file(filename):
    import pretty_midi
    import numpy as np
    # Create a PrettyMIDI object
    midi_data = pretty_midi.PrettyMIDI()
    # Create an Instrument instance
    instrument1 = pretty_midi.Instrument(program=0)
    instrument2 = pretty_midi.Instrument(program=10)
    instruments = [instrument1, instrument2]

    pitches = [60, 64, 67]
    times = [(0, 1), (1, 2), (2, 3), (3, 4)]
    for instrument in instruments:
        # Iterate over note names, which will be converted to note number later
        for start, end in times:
            for pitch in pitches:
                # Create a Note instance, starting at 0s and ending at 1s
                note = pretty_midi.Note(
                    velocity=100, pitch=pitch, start=start, end=end)
                # Add it to our instrument
                instrument.notes.append(note)
        # Add the instrument to the PrettyMIDI object
        midi_data.instruments.append(instrument)
        # Write out the MIDI data
    midi_data.write(filename)

def test_empty_midi_score():
    """ """
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120

    )

    assert score.shape == (2, 4)

    # Assert still same shape if writing and loading it
    new_score = MidiScore.from_base64(score.to_base64())

    assert new_score.shape == (2, 4)


def test_add_track():
    """ """
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120

    )

    new_score = score.add_instrument(instrument.PIANO)

    assert new_score.shape == (3, 4)


def test_get_item_track_slice():
    """ """
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120

    )
    new_score = score[1:]
    assert new_score.shape == (1, 4)

    program, is_drum = INSTRUMENTS_DICT[instrument.VIOLIN]
    assert new_score.track_keys == [(1, program, is_drum) ]
    assert len(new_score.tracks) == 1

    new_score = score[:1]
    assert new_score.shape == (1, 4)
    assert len(new_score.tracks) == 1
    program, is_drum = INSTRUMENTS_DICT[instrument.PIANO]
    assert new_score.track_keys == [(0, program, is_drum)]

    new_score = score[:]
    assert new_score.shape == (2, 4)
    assert len(new_score.tracks) == 2
    program1, is_drum1 = INSTRUMENTS_DICT[instrument.PIANO]
    program2, is_drum2 = INSTRUMENTS_DICT[instrument.VIOLIN]
    assert new_score.track_keys == [(0, program1, is_drum1), (1, program2, is_drum2)]

def test_get_item_chord_slice():
    """ """
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120

    )
    new_score = score[:, 1:]
    assert new_score.shape == (2, 3)

    new_score = score[:, :1]
    assert new_score.shape == (2, 1)

    new_score = score[:, :]
    assert new_score.shape == (2, 4)


def test_set_item_single_track():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )
    other_score = MidiScore.from_empty(
        instruments=[instrument.FLUTE],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    # Modify the other track
    other_score.tracks[other_score.track_keys[0]][0]['time'][0] += 2

    score[0, :] = other_score
    assert score.track_keys[0] == (0, INSTRUMENTS_DICT[instrument.PIANO][0], INSTRUMENTS_DICT[instrument.PIANO][1] == 1)
    assert score.get_track_from_index(0) == other_score.get_track_from_index(0)


def test_set_item_multiple_slice():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )
    other_score = MidiScore.from_empty(
        instruments=[instrument.FLUTE],
        nb_bars=3,
        ts=(4, 4),
        tempo=120
    )

    # Modify the other track
    other_score.tracks[other_score.track_keys[0]][2]['time'][0] += 2

    score[1:, 1:] = other_score
    assert score.track_keys[1] == (1, INSTRUMENTS_DICT[instrument.VIOLIN][0], INSTRUMENTS_DICT[instrument.VIOLIN][1] == 1)
    assert score[:, 1:].get_track_from_index(1) == other_score.get_track_from_index(0)

def test_set_item_invalid_type():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    with pytest.raises(TypeError):
        score[0, 0] = "not a MidiScore"