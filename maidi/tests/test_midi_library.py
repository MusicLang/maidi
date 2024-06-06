
from maidi import midi_library


def test_midi_library_list():
    files = midi_library.get_list_of_midi_files()
    assert len(files) > 0


def test_midi_library_get_works():
    files = midi_library.get_list_of_midi_files()
    file = midi_library.get_midi_file(files[0])
    assert file is not None
