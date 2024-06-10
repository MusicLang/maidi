
from maidi.midi_library import get_list_of_midi_files,get_midi_file
from maidi import MidiScore, instrument
from maidi.constants import INSTRUMENTS_DICT


def test_horizontal_concatenation():
    midi_file = get_list_of_midi_files()[0]
    score1 = MidiScore.from_midi(get_midi_file(midi_file))
    score2 = MidiScore.from_midi(get_midi_file(midi_file))

    shape1 = score1.shape

    new_score = score1.concatenate(score2, axis=1)

    assert new_score.shape[1] == shape1[1] * 2

    assert new_score.bars == score1.bars + score2.bars

def test_vertical_concatenation():
    midi_file = get_list_of_midi_files()[0]
    score1 = MidiScore.from_midi(get_midi_file(midi_file))
    score2 = MidiScore.from_midi(get_midi_file(midi_file))

    shape1 = score1.shape

    new_score = score1.concatenate(score2, axis=0)

    assert new_score.shape[0] == shape1[0] * 2


def test_vertical_concatenation_good_instruments():
    score1 = MidiScore.from_empty(instruments=[instrument.VIOLIN, instrument.CELLO],
                                  nb_bars=4)
    score2 = MidiScore.from_empty(instruments=[instrument.PIANO, instrument.FLUTE],
                                  nb_bars=score1.nb_bars )

    shape1 = score1.shape
    nb_instruments = shape1[0]
    new_score = score1.concatenate(score2, axis=0)

    assert new_score.shape[0] == shape1[0] + score2.shape[0]
    assert new_score.track_keys[-2:] == [(nb_instruments, *INSTRUMENTS_DICT[instrument.PIANO]),
                                         (nb_instruments + 1, *INSTRUMENTS_DICT[instrument.FLUTE])]


def test_horizontal_concatenation_good_instruments():
    score1 = MidiScore.from_empty(instruments=[instrument.VIOLIN, instrument.CELLO],
                                  nb_bars=4)
    score2 = MidiScore.from_empty(instruments=[instrument.PIANO, instrument.FLUTE],
                                  nb_bars=4 )

    shape1 = score1.shape
    new_score = score1.concatenate(score2, axis=1)

    assert new_score.shape[1] == shape1[1] + score2.shape[1]
    assert new_score.track_keys == [(0, *INSTRUMENTS_DICT[instrument.VIOLIN]),
                                         (1, *INSTRUMENTS_DICT[instrument.CELLO])]