import pytest
from maidi import TagManager, MidiScore, instrument

@pytest.fixture
def setup_score():
    return get_2_2_score()

def get_2_2_score():
    # 2 tracks, 2 bars
    instruments = [instrument.PIANO, instrument.ELECTRIC_BASS_FINGER]
    score = MidiScore.from_empty(instruments=instruments, nb_bars=2, ts=(4, 4), tempo=120)
    return score


def test_tag_manager_shape(setup_score):
    score = setup_score
    tag_manager = TagManager.empty_from_score(score)
    assert len(tag_manager) == 2
    assert tag_manager.shape == (2, 2)



@pytest.fixture
def tag_manager():
    tags = [
        [["tag1", "tag2"], ["tag3"]],
        [["tag4"], ["tag5", "tag6"]]
    ]
    return TagManager(tags)

@pytest.fixture
def empty_tag_manager():
    return TagManager.empty_from_score(get_2_2_score())

def test_init(tag_manager):
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["tag3"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_empty_from_score(empty_tag_manager):
    assert empty_tag_manager.tags == [[[], []], [[], []]]

def test_add_tag(tag_manager):
    tag_manager.add_tag("new_tag")
    assert tag_manager.tags == [
        [["tag1", "tag2", "new_tag"], ["tag3", "new_tag"]],
        [["tag4", "new_tag"], ["tag5", "tag6", "new_tag"]]
    ]

def test_add_tags(tag_manager):
    tag_manager.add_tags(["new_tag1", "new_tag2"])
    assert tag_manager.tags == [
        [["tag1", "tag2", "new_tag1", "new_tag2"], ["tag3", "new_tag1", "new_tag2"]],
        [["tag4", "new_tag1", "new_tag2"], ["tag5", "tag6", "new_tag1", "new_tag2"]]
    ]

def test_add_tag_at_index(tag_manager):
    tag_manager.add_tag_at_index("new_tag", 0, 1)
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["tag3", "new_tag"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_add_tags_at_index(tag_manager):
    tag_manager.add_tags_at_index(["new_tag1", "new_tag2"], 0, 1)
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["tag3", "new_tag1", "new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_add_tag_for_track(tag_manager):
    tag_manager.add_tag_for_track("new_tag", 0)
    assert tag_manager.tags == [
        [["tag1", "tag2", "new_tag"], ["tag3", "new_tag"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_add_tags_for_track(tag_manager):
    tag_manager.add_tags_for_track(["new_tag1", "new_tag2"], 0)
    assert tag_manager.tags == [
        [["tag1", "tag2", "new_tag1", "new_tag2"], ["tag3", "new_tag1", "new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_add_tags_for_bar(tag_manager):
    tag_manager.add_tags_for_bar(["new_tag1", "new_tag2"], 0)
    assert tag_manager.tags == [
        [["tag1", "tag2", "new_tag1", "new_tag2"], ["tag3"]],
        [["tag4", "new_tag1", "new_tag2"], ["tag5", "tag6"]]
    ]

def test_add_tag_for_bar(tag_manager):
    tag_manager.add_tag_for_bar("new_tag", 1)
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["tag3", "new_tag"]],
        [["tag4"], ["tag5", "tag6", "new_tag"]]
    ]

def test_remove_tag(tag_manager):
    tag_manager.remove_tag("tag1")
    assert tag_manager.tags == [
        [["tag2"], ["tag3"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_remove_tags(tag_manager):
    tag_manager.remove_tags(["tag1", "tag2", "tag3"])
    assert tag_manager.tags == [
        [[], []],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_remove_tag_for_track(tag_manager):
    tag_manager.remove_tag_for_track("tag4", 1)
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["tag3"]],
        [[], ["tag5", "tag6"]]
    ]

def test_remove_tags_for_track(tag_manager):
    tag_manager.remove_tags_for_track(["tag5", "tag6"], 1)
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["tag3"]],
        [["tag4"], []]
    ]

def test_remove_tag_at_index(tag_manager):
    tag_manager.remove_tag_at_index("tag1", 0, 0)
    assert tag_manager.tags == [
        [["tag2"], ["tag3"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_remove_tags_at_index(tag_manager):
    tag_manager.remove_tags_at_index(["tag1", "tag2"], 0, 0)
    assert tag_manager.tags == [
        [[], ["tag3"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_remove_tags_for_bar(tag_manager):
    tag_manager.remove_tags_for_bar(["tag1", "tag2"], 0)
    assert tag_manager.tags == [
        [[], ["tag3"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_remove_tag_for_bar(tag_manager):
    tag_manager.remove_tag_for_bar("tag5", 1)
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["tag3"]],
        [["tag4"], ["tag6"]]
    ]

def test_shape(tag_manager):
    assert tag_manager.shape == (2, 2)

def test_len(tag_manager):
    assert len(tag_manager) == 2

def test_getitem(tag_manager):
    assert tag_manager[0].tags == [[["tag1", "tag2"], ["tag3"]]]
    assert tag_manager[0, 1].tags == [[["tag3"]]]
    assert tag_manager[:, 1].tags == [[["tag3"]], [["tag5", "tag6"]]]

def test_getitem_errors(tag_manager):
    with pytest.raises(ValueError) as e:
        tag_manager[(0, 1, 2)]
    assert "Item should be a tuple of length 2" in str(e.value)


def test_setitem_single_track(tag_manager):
    tag_manager[0] = TagManager([[["new_tag1"], ["new_tag2"]]])
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_single_track_string(tag_manager):
    tag_manager[0] = "new_tag"
    assert tag_manager.tags == [
        [["new_tag"], ["new_tag"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_single_track_list(tag_manager):
    tag_manager[0] = ["new_tag1", "new_tag2"]
    assert tag_manager.tags == [
        [["new_tag1", "new_tag2"], ["new_tag1", "new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_single_track_list_of_lists(tag_manager):
    tag_manager[0] = [["new_tag1"], ["new_tag2"]]
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_slice(tag_manager):
    tag_manager[0:2] = TagManager([
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ])
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ]

def test_setitem_slice_string(tag_manager):
    tag_manager[0:2] = "new_tag"
    assert tag_manager.tags == [
        [["new_tag"], ["new_tag"]],
        [["new_tag"], ["new_tag"]]
    ]

def test_setitem_slice_list(tag_manager):
    tag_manager[0:2] = ["new_tag1", "new_tag2"]
    assert tag_manager.tags == [
        [["new_tag1", "new_tag2"], ["new_tag1", "new_tag2"]],
        [["new_tag1", "new_tag2"], ["new_tag1", "new_tag2"]]
    ]

def test_setitem_slice_list_of_lists(tag_manager):
    tag_manager[0:2] = TagManager([
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ])
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ]


def test_setitem_slice_list_of_lists_minus(tag_manager):
    tag_manager[0:-1] = TagManager([
        [["new_tag1"], ["new_tag2"]],
    ])
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]


def test_setitem_slice_list_of_lists_sublist(tag_manager):
    tag_manager[0:1] = TagManager([
        [["new_tag1"], ["new_tag2"]],
    ])
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]


def test_setitem_slice_list_of_lists_with_no_tag_manager(tag_manager):
    tag_manager[0:2, :] = [
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ]
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ]


def test_setitem_tuple_single_cell(tag_manager):
    tag_manager[0, 1] = "new_tag"
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["new_tag"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_tuple_single_cell_list(tag_manager):
    tag_manager[0, 1] = ["new_tag1", "new_tag2"]
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["new_tag1", "new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_tuple_slice_of_bars(tag_manager):
    tag_manager[0, 0:2] = TagManager([[["new_tag1"], ["new_tag2"]]])
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_tuple_slice_of_bars_string(tag_manager):
    tag_manager[0, 0:2] = "new_tag"
    assert tag_manager.tags == [
        [["new_tag"], ["new_tag"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_tuple_slice_of_bars_list(tag_manager):
    tag_manager[0, 0:2] = ["new_tag1", "new_tag2"]
    assert tag_manager.tags == [
        [["new_tag1", "new_tag2"], ["new_tag1", "new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_tuple_slice_of_bars_list_of_lists(tag_manager):
    tag_manager[0, 0:2] = [["new_tag1"], ["new_tag2"]]
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["tag4"], ["tag5", "tag6"]]
    ]

def test_setitem_tuple_single_bar_across_tracks(tag_manager):
    tag_manager[:, 1] = TagManager([
        [["new_tag1"]],
        [["new_tag2"]]
    ])
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["new_tag1"]],
        [["tag4"], ["new_tag2"]]
    ]


def test_setitem_all(tag_manager):
    tag_manager[:, :] = TagManager([
        [["new_tag1"], ["new_tag2"]],
        [["new_tag2"], ["new_tag3"]]
    ])
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["new_tag2"], ["new_tag3"]]
    ]

def test_setitem_all_with_one_string(tag_manager):
    tag_manager[:, :] = 'new_tag'
    assert tag_manager.tags == [
        [["new_tag"], ["new_tag"]],
        [["new_tag"], ["new_tag"]]
    ]

def test_setitem_tuple_single_bar_across_tracks_string(tag_manager):
    tag_manager[0:2, 1] = "new_tag"
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["new_tag"]],
        [["tag4"], ["new_tag"]]
    ]

def test_setitem_tuple_single_bar_across_tracks_list(tag_manager):
    tag_manager[0:2, 1] = ["new_tag1", "new_tag2"]
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["new_tag1", "new_tag2"]],
        [["tag4"], ["new_tag1", "new_tag2"]]
    ]

def test_setitem_tuple_slice_of_bars_across_tracks(tag_manager):
    tag_manager[0:2, 0:2] = TagManager([
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ])
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ]

def test_setitem_tuple_slice_of_bars_across_tracks_string(tag_manager):
    tag_manager[0:2, 0:2] = "new_tag"
    assert tag_manager.tags == [
        [["new_tag"], ["new_tag"]],
        [["new_tag"], ["new_tag"]]
    ]

def test_setitem_tuple_slice_of_bars_across_tracks_list(tag_manager):
    tag_manager[0:2, 0:2] = ["new_tag1", "new_tag2"]
    assert tag_manager.tags == [
        [["new_tag1", "new_tag2"], ["new_tag1", "new_tag2"]],
        [["new_tag1", "new_tag2"], ["new_tag1", "new_tag2"]]
    ]

def test_setitem_tuple_slice_of_bars_across_tracks_list_of_lists(tag_manager):
    tag_manager[0:2, 0:2] = [
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ]
    assert tag_manager.tags == [
        [["new_tag1"], ["new_tag2"]],
        [["new_tag3"], ["new_tag4"]]
    ]

def test_add_bars(tag_manager):
    tag_manager.add_bars(1)
    assert tag_manager.tags == [
        [["tag1", "tag2"], ["tag3"], []],
        [["tag4"], ["tag5", "tag6"], []]
    ]

def test_empty():
    tag_manager = TagManager.empty(2, 2)
    assert tag_manager.tags == [[[], []], [[], []]]