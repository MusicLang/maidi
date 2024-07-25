from maidi import ChordManager
import pytest


def test_chord_manager_with_none():

    chords = [None, None, (0, 0, 'M', ''), (0, 1, 'M', '6')]

    cm = ChordManager(chords)

    assert cm[0] == None

    new_chords = cm.to_chords()
    assert new_chords == chords

    cm[1:3] = [(0, 2, 'm', ''), None]
    assert cm.to_chords() == [None, (0, 2, 'm', ''), None, (0, 1, 'M', '6')]

    with pytest.raises(ValueError) as e:
        cm[0:3] = [(0, 2, 'm', ''), None]
    assert "Wrong number of chords assigned" in str(e.value)


def test_chord_manager_set_item():
    chords = [None, (0, 0, 'M', ''), (0, 1, 'M', '6')]
    cm = ChordManager(chords)

    cm[0] = (0, 0, 'M', '7')

    assert cm[0] == (0, 0, 'M', '7')

    cm[1:3] = [(0, 0, 'M', '7'), (0, 1, 'M', '7')]



    assert cm[1] == (0, 0, 'M', '7')
    assert cm[2] == (0, 1, 'M', '7')

    cm[0] = None
    assert cm[0] == None