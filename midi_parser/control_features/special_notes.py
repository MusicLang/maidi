
from .parse_notes import parse_pitch


INTERESTING_NOTES = [
    ('s', 1),
    ('s', 3),
    ('s', 5),
    ('h', 1),
    ('h', 2),
    ('h', 3),
    ('h', 4),
    ('h', 6),
    ('h', 8),
    ('h', 9),
    ('h', 10),
    ('h', 11),
]

def get_token_names():
    return ['CONTROL_SPECIAL_NOTE__' + note + str(idx) for note, idx in INTERESTING_NOTES]


def get_special_notes_tags(track_bar, chord):
    """
    Create histogram of (type, idx) weighted per duration
    :param track_bar:
    :param chord:
    :return:
    """
    notes = []
    for idx_note in range(len(track_bar['time'])):
        pitch = track_bar['pitch'][idx_note]
        velocity = track_bar['velocity'][idx_note]
        time = track_bar['time'][idx_note]
        duration = track_bar['duration'][idx_note]
        type, idx, oct = parse_pitch(pitch, chord, False,
                                     is_absolute=False)
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


def get_special_notes_tokens(track_bar, chord):
    special_notes = get_special_notes_tags(track_bar, chord)
    return ['CONTROL_SPECIAL_NOTE__' + note + str(idx) for note, idx in special_notes]

