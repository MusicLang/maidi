from maidi.analysis.control_features import get_min_max_registers


def test_get_min_max_registers():
    """ """
    assert get_min_max_registers([30, 40, 50]) == ["lowest", "contrabass"]
    assert get_min_max_registers([80, 90, 100]) == ["sopranissimo", "highest"]
    assert get_min_max_registers([45, 55, 65]) == ["baritone", "baritone"]
    assert get_min_max_registers([53, 74]) == ["contralto", "contralto"]
    assert get_min_max_registers([41, 42, 43]) == ["bass", "bass"]
    assert get_min_max_registers([0, 1, 2]) == ["lowest", "lowest"]
    assert get_min_max_registers([60, 130]) == ["soprano", "highest"]
    assert get_min_max_registers([36, 57]) == ["contrabass", "contrabass"]


def test_get_min_max_registers_empty():
    """ """
    assert get_min_max_registers([]) == []
