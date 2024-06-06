from maidi.utils.bar_helpers import bar_to_bar_duration_in_ticks, bar_to_bar_duration_in_quarters


def test_bar_to_bar_duration_in_ticks():
    bar = [0, 0, 'm', -1, '', 3, 4, 0] # 3/4
    assert bar_to_bar_duration_in_ticks(bar, tpq=24) == 72

def test_bar_to_bar_duration_in_quarters():
    bar = [0, 0, 'm', -1, '', 4, 4, 0]
    assert bar_to_bar_duration_in_quarters(bar) == 4

    bar = [0, 0, 'm', -1, '', 3, 8, 0]
    assert bar_to_bar_duration_in_quarters(bar) == 1.5

