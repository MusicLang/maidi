
from maidi.analysis import TagsProvider


MAX_MIN_POLYPHONY = 6
MAX_MAX_POLYPHONY = 6

def get_tags_names():
    """

    Returns
    -------

    """
    return [
        "CONTROL_MIN_POLYPHONY__" + str(i) for i in range(MAX_MIN_POLYPHONY)
    ] + [
        "CONTROL_MAX_POLYPHONY__" + str(i) for i in range(MAX_MAX_POLYPHONY)
    ]


class MinMaxPolyphonyTagsProvider(TagsProvider):
    ALL_TAGS = get_tags_names()

    def get_tags(self, track_bar, chord, score):
        notes = self.get_start_end_notes(track_bar, chord, score)
        return get_min_max_polyphony_tags(notes)

def get_max_polyphony(notes):
    """

    Parameters
    ----------
    notes :
        

    Returns
    -------

    """
    if not notes:
        return 0

    events = []
    for start, end in notes:
        events.append((start, "start"))
        events.append((end, "end"))

    # Sort events, ensuring end events come before start events if they are at the same time
    events.sort(key=lambda x: (x[0], x[1] == "start"))

    max_count = 0
    current_count = 0

    for time, event_type in events:
        if event_type == "start":
            current_count += 1
            max_count = max(max_count, current_count)
        elif event_type == "end":
            current_count -= 1

    return max_count


def get_min_polyphony(notes):
    """

    Parameters
    ----------
    notes :
        

    Returns
    -------

    """
    if not notes:
        return 0

    events = []
    for start, end in notes:
        events.append((start, "start"))
        events.append((end, "end"))

    # Sort events with end events before start if at the same time to ensure a note ending and starting at the same time is not counted twice
    events.sort(key=lambda x: (x[0], x[1] == "start"))

    # (1, start), (1, start), (1, start), (1, end), (1, end), (1, end)
    current_count = 0
    min_count = float("inf")
    prev_time = 0
    # Process each event
    for time, event_type in events:
        if event_type == "start":
            current_count += 1
        else:  # event_type == 'end'
            # Check for non-zero counts to track the minimum before decrementing
            if current_count > 0 and prev_time != time:
                min_count = min(min_count, current_count)
                prev_time = time
            current_count -= 1

    # If min_count was never updated, return 0, otherwise, return min_count
    return min_count if min_count != float("inf") else 0




def get_min_polyphony_tags(notes):
    """

    Parameters
    ----------
    notes :
    """

    return ["CONTROL_MIN_POLYPHONY__" + str(get_min_polyphony(notes))]

def get_max_polyphony_tags(notes):
    """

    Parameters
    ----------
    notes :


    Returns
    -------

    """
    return ["CONTROL_MAX_POLYPHONY__" + str(get_max_polyphony(notes))]

def get_min_max_polyphony_tags(notes):
    """

    Parameters
    ----------
    notes :


    Returns
    -------

    """
    return get_min_polyphony_tags(notes) + get_max_polyphony_tags(notes)