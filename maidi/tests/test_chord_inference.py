from maidi.chords.chord_inference import fast_chord_inference

def test_chord_inference():

    tracks = {(0, 0, 0): [
        {"pitch": [60, 64, 67], "time": [0, 0, 0], "duration": [1, 1, 1]},
        {"pitch": [59, 62, 67], "time": [2, 2, 2], "duration": [1, 1, 1]},
        {"pitch": [60, 64, 67], "time": [2, 2, 2], "duration": [1, 1, 1]}
    ]}

    chord_durations = [(4, 4), (4, 4), (4, 4)]
    chords = fast_chord_inference(tracks, chord_durations)
    expected_chords = [(0, 0, 'M', 0, '', 4, 4), (4, 0, 'M', -1, '6', 4, 4), (0, 0, 'M', 0, '', 4, 4)]

    assert chords == expected_chords