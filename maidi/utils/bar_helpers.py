

def bar_to_bar_duration_in_ticks(bar, tpq=24):
    """
    From a bar, returns the duration of a bar in ticks
    :param bar:
    :return:
    """
    from maidi import MidiScore

    ts_num = bar[MidiScore.TIME_SIGNATURE_NUMERATOR_INDEX]
    ts_den = bar[MidiScore.TIME_SIGNATURE_DENOMINATOR_INDEX]
    return tpq * 4 * ts_num / ts_den

def bar_to_bar_duration_in_quarters(bar):
    """
    From a bar, returns the duration of a bar in ticks
    :param bar:
    :return:
    """
    from maidi import MidiScore

    ts_num = bar[MidiScore.TIME_SIGNATURE_NUMERATOR_INDEX]
    ts_den = bar[MidiScore.TIME_SIGNATURE_DENOMINATOR_INDEX]
    return 4 * ts_num / ts_den