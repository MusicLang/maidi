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


def test_setitem_entire_track():
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

    score[0] = other_score
    assert score.track_keys[0] == (0, INSTRUMENTS_DICT[instrument.PIANO][0], INSTRUMENTS_DICT[instrument.PIANO][1] == 1)
    assert score.get_track_from_index(0) == other_score.get_track_from_index(0)

def test_setitem_entire_track_more_than_one_track():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )
    other_score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    # Assert it raises an error
    with pytest.raises(ValueError) as e:
        score[0] = other_score
    assert  "The provided MidiScore must have one track" in str(e.value)


def test_setitem_entire_track_wrong_bar_number():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )
    other_score = MidiScore.from_empty(
        instruments=[instrument.PIANO],
        nb_bars=3,
        ts=(4, 4),
        tempo=120
    )

    # Assert it raises an error
    with pytest.raises(ValueError) as e:
        score[0] = other_score
    assert "The provided MidiScore must have the same number of bars" in str(e.value)


def test_setitem_assign_slice():

    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )
    other_score = MidiScore.from_empty(
        instruments=[instrument.PIANO],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    # Modify the other track
    other_score.tracks[other_score.track_keys[0]][0]['time'][0] += 2

    score[1:] = other_score
    assert score.track_keys[1] == (1, INSTRUMENTS_DICT[instrument.VIOLIN][0], INSTRUMENTS_DICT[instrument.VIOLIN][1] == 1)
    assert score.get_track_from_index(1) == other_score.get_track_from_index(0)

def test_setitem_assign_slice_wrong_bar_number():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )
    other_score = MidiScore.from_empty(
        instruments=[instrument.PIANO],
        nb_bars=5,
        ts=(4, 4),
        tempo=120
    )

    # Assert it raises an error
    with pytest.raises(ValueError) as e:
        score[1:] = other_score
    assert "The provided MidiScore must have the same number of bars" in str(e.value)

def test_setitem_assign_slice_wrong_track_number():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )
    other_score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=3,
        ts=(4, 4),
        tempo=120
    )

    # Assert it raises an error
    with pytest.raises(ValueError) as e:
        score[1:] = other_score
    assert "The provided MidiScore must have the same number of tracks" in str(e.value)


def test_wrong_index_type_setitem():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )


    with pytest.raises(TypeError):
        score["a"] = score[1]

def test_wrong_shape_setitem_tuple():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    with pytest.raises(ValueError) as e:
        score[0, 0] = score[1]
    assert "Shapes do not match" in str(e.value)



def test_setitem_tuple_second_dim_int():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )
    score[:, 0] = score[:, 1]

    score[0, :] = score[1, :]

    score[:, :-1] = score[:, 1:]

    score[:-1, :] = score[1:, :]

def test_different_shape_of_getitem():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    assert score[:, 1:].shape == (2, 3)

    assert score[:, :1].shape == (2, 1)

    assert score[1:2, 1:].shape == (1, 3)

    assert score[-2:-1, 1:].shape == (1, 3)

    assert score[0, :].shape == (1, 4)



def test_assign_tracks_bar_range_none():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    other_score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    score.assign_tracks([0, 1], other_score, bar_range=None)


def test_get_chords_prompts():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    chord_prompt = score.get_chords_prompt()
    assert len(chord_prompt) == 4
    assert len(chord_prompt[0]) == 4


def test_get_bars_int():

    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    new_score = score.get_bars(1)
    assert new_score.shape == (2, 1)

def test_get_tracks_int():

    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120
    )

    new_score = score.get_tracks(1)
    assert new_score.shape == (1, 4)

def test_add_note():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO],
        nb_bars=4,
        ts=(4, 4),
        tempo=120,
        add_fake_notes=False
    )
    score = score.add_note(60, 3, 10, 40, 0, 1)
    track = (0, 0, 0) # Piano
    assert len(score.tracks[track][1]['time']) == 1
    assert score.tracks[track][1]['pitch'][0] == 60
    assert score.tracks[track][1]['time'][0] == 3
    assert score.tracks[track][1]['duration'][0] == 10
    assert score.tracks[track][1]['velocity'][0] == 40



def test_delete_bar():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO],
        nb_bars=4,
        ts=(4, 4),
        tempo=120,
        add_fake_notes=False
    )
    score = score.delete_bar(3)
    assert score.shape == (1, 3)


def test_get_bar_duration():
    score1 = MidiScore.from_empty(
        instruments=[instrument.PIANO],
        nb_bars=2,
        ts=(4, 4),
        tempo=120,
        add_fake_notes=False,
        tpq=24
    )
    score2 = MidiScore.from_empty(
        instruments=[instrument.PIANO],
        nb_bars=4,
        ts=(3, 4),
        tempo=120,
        add_fake_notes=False,
        tpq=24
    )
    score = score1.concatenate(score2, axis=1)

    assert score.get_bar_duration(0) == 4 * 24
    assert score.get_bar_duration(1) == 4 * 24
    assert score.get_bar_duration(2) == 3 * 24
    assert score.get_bar_duration(3) == 3 * 24


def test_write_read_empty_score():

    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120,
        add_fake_notes=True
    )

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=True) as f:
        score.write(f.name)
        new_score = MidiScore.from_midi(f.name)
        assert new_score.nb_bars == 4



def test_prevent_silence_tags():

    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120,
        add_fake_notes=True
    )

    mask, tags, chords = score.get_empty_controls(prevent_silence=False)
    new_tags = MidiScore.prevent_silence_tags(tags)

    assert new_tags[0][0][0] == 'CONTROL_MIN_POLYPHONY__1'


def test_get_empty_controls():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120,
    )

    mask, tags, chords = score.get_empty_controls()
    assert mask.shape == (2, 4)
    assert len(tags) == 2
    assert len(tags[0]) == 4
    assert len(chords) == 4


def test_get_silenced_mask():
    import numpy as np
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=4,
        ts=(4, 4),
        tempo=120,
    )
    score = score.add_note(60, 0, 10, 30, 1, 1)
    silence_mask = score.get_silenced_mask()
    print(silence_mask)
    assert silence_mask[1, 1] == 0

    silence_mask[1, 1] = 1
    assert np.min(silence_mask) == 1

def test_cut_silenced_bars_at_beginning_and_end():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=3,
        ts=(4, 4),
        tempo=120,
    )

    # Add a note on second bar
    score = score.add_note(60, 1, 10, 30, 0, 1)

    # Cut the first and last bar
    score = score.cut_silenced_bars_at_beginning_and_end()

    assert score.nb_bars == 1


def test_check_mask():

    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=3,
        ts=(4, 4),
        tempo=120,
    )

    mask = score.get_mask()


    with pytest.raises(ValueError) as e:
        score.check_mask(mask[:-1, :])
    assert "Mask number of tracks does not match score number of tracks" in str(e.value)

    with pytest.raises(ValueError) as e:
        score.check_mask(mask[:, :-1])
    assert "Mask length does not match score length" in str(e.value)

    with pytest.raises(ValueError) as e:
        score.check_mask(mask)
    assert "Mask must have at least one 1" in str(e.value)


def test_check_times():

    score = MidiScore.from_empty(

        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=3,
        ts=(4, 4),
        tempo=120,
    )

    score.bars.append(score.bars[-1])

    with pytest.raises(ValueError) as e:
        score.check_times()
    assert "Track and bar length mismatch" in str(e.value)


def test_add_instrument_wrong_instrument():
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=3,
        ts=(4, 4),
        tempo=120,
    )

    with pytest.raises(ValueError) as e:
        score.add_instrument("Unknown instrument")
    assert "Unknown instrument" in str(e.value)


def test_add_instrument_twice_is_ok():

    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.VIOLIN],
        nb_bars=3,
        ts=(4, 4),
        tempo=120,
    )
    score = score.add_instrument(instrument.PIANO)
    assert score.nb_tracks == 3
    score = score.add_instrument(instrument.PIANO)
    assert score.nb_tracks == 4



