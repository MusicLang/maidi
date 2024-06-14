from maidi.analysis.parse_notes import parse_pitch, to_pitch, get_amp_figure, amp_figure_to_velocity, pitch_to_note_type

###################

## Write the test functions below

def test_parse_pitch():
    assert parse_pitch(60, (0, 2, 'm', 0, '', 4, 4), False, False) == ('h', 10, -1)
    assert parse_pitch(60, (0, 2, 'm', 0, '', 4, 4), False, True) == ('a', 0, 0)
    assert parse_pitch(61, (0, 2, 'm', 0, '', 4, 4), True, False) == ('d', 1, 0)
    assert parse_pitch(50, (0, 2, 'm', 0, '', 4, 4), False, False) == ('s', 0, -1)

def test_to_pitch():

    assert to_pitch('s', 1, -1, (0, 0, 'm', 0, '', 4, 4)) == 50
    assert to_pitch('h', 10, -1, (0, 0, 'm', 0, '', 4, 4)) == 58
    assert to_pitch('a', 0, 0, (0, 1, 'm', 0, '', 4, 4)) == 60
    assert to_pitch('d', 1, 0, (0, 1, 'm', 0, '', 4, 4)) == 61


def test_get_amp_figure():

    assert get_amp_figure(0) == "n"
    assert get_amp_figure(127) == 'fff'

    velocity = amp_figure_to_velocity("f")
    assert amp_figure_to_velocity(get_amp_figure(velocity))  == velocity


def test_pitch_to_note_type():

    pitch = 60
    velocity = 127
    time = 0
    duration = 1
    chord = (0, 2, 'm', 0, '', 4, 4)
    is_drum = False
    is_absolute = False

    type, idx, oct, amp, time, duration = pitch_to_note_type(pitch, velocity, time, duration, chord, is_drum, is_absolute)

    assert (type, idx, oct, amp, time, duration) == ('h', 10, -1, 'fff', 0, 1)
