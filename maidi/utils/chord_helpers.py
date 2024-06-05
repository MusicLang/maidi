

def chord_to_bar_duration_in_ticks(chord, tpq=24):
    """
    From a chord, returns the duration of a bar in ticks
    :param chord:
    :return:
    """
    from maidi import MidiScore

    ts_num = chord[MidiScore.TIME_SIGNATURE_NUMERATOR_INDEX]
    ts_den = chord[MidiScore.TIME_SIGNATURE_DENOMINATOR_INDEX]
    return tpq * 4 * ts_num / ts_den

def chord_to_bar_duration_in_quarters(chord):
    """
    From a chord, returns the duration of a bar in ticks
    :param chord:
    :return:
    """
    from maidi import MidiScore

    ts_num = chord[MidiScore.TIME_SIGNATURE_NUMERATOR_INDEX]
    ts_den = chord[MidiScore.TIME_SIGNATURE_DENOMINATOR_INDEX]
    return 4 * ts_num / ts_den