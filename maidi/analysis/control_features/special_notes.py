from maidi.analysis.parse_notes import parse_pitch
from maidi.analysis import TagsProvider

INTERESTING_NOTES = [
    ("s", 1),  # The second note of the scale (9)
    ("s", 3), # The fourth note of the scale (11)
    ("s", 5), # The sixth note of the scale (13)
    ("h", 1), # The second note of the chromatic scale (b9)
    ("h", 2), # The third note of the chromatic scale (9)
    ("h", 3), # The fourth note of the chromatic scale (#9)
    ("h", 4), # The fifth note of the chromatic scale (natural 3)
    ("h", 6), # The seventh note of the chromatic scale (b5)
    ("h", 8), # The ninth note of the chromatic scale (b6)
    ("h", 9), # The tenth note of the chromatic scale (natural 6)
    ("h", 10), # The eleventh note of the chromatic scale (b7)
    ("h", 11), # The twelfth note of the chromatic scale (natural 7)
]


def get_tags_names():
    """ """
    return [
        "CONTROL_SPECIAL_NOTE__" + note + str(idx) for note, idx in INTERESTING_NOTES
    ]


class SpecialNotesTagsProvider(TagsProvider):
    ALL_TAGS = get_tags_names()

    def get_tags(self, track_bar, chord, score):
        return get_special_notes_tags(track_bar, chord)

def _get_special_notes_tags(track_bar, chord):
    """Create histogram of (type, idx) weighted per duration

    Parameters
    ----------
    track_bar :
        param chord:
    chord :
        

    Returns
    -------

    """
    notes = []
    for idx_note in range(len(track_bar["time"])):
        pitch = track_bar["pitch"][idx_note]
        velocity = track_bar["velocity"][idx_note]
        time = track_bar["time"][idx_note]
        duration = track_bar["duration"][idx_note]
        type, idx, oct = parse_pitch(pitch, chord, False, is_absolute=False)
        notes.append((type, idx, oct, velocity, time, duration))

    # Create histogram of (type, idx) weighted per duration
    special_notes = {}
    for note in notes:
        type, idx, oct, velocity, time, duration = note
        if (type, idx) not in special_notes:
            special_notes[(type, idx)] = 0
        special_notes[(type, idx)] += duration

    # Normalize
    total_duration = sum([duration for duration in special_notes.values()])
    for key in special_notes:
        special_notes[key] /= total_duration

    # Find top 3, find if interesting notes in this top, if so returns it
    top_notes = sorted(special_notes.items(), key=lambda x: x[1], reverse=True)[:3]
    interesting_notes = []
    for note, weight in top_notes:
        if note in INTERESTING_NOTES:
            interesting_notes.append(note)
    return interesting_notes


def get_special_notes_tags(track_bar, chord):
    """

    Parameters
    ----------
    track_bar :
        
    chord :
        

    Returns
    -------

    """
    special_notes = _get_special_notes_tags(track_bar, chord)
    return ["CONTROL_SPECIAL_NOTE__" + note + str(idx) for note, idx in special_notes]
