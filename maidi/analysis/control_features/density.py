from maidi import MidiScore
from maidi.analysis import TagsProvider


def get_tags_names():
    """ """
    return [
        "CONTROL_DENSITY__" + density
        for density in [
            "LOWEST",
            "LOWER",
            "LOW",
            "MEDIUM_LOW",
            "MEDIUM",
            "HIGH",
            "VERY_HIGH",
        ]
    ]


class DensityTagsProvider(TagsProvider):
    ALL_TAGS = get_tags_names()

    def get_tags(self, track_bar, chord, score):
        from maidi.utils.bar_helpers import bar_to_bar_duration_in_quarters
        notes = self.get_start_end_notes(track_bar, chord, score)
        bar_duration = bar_to_bar_duration_in_quarters(chord)
        return get_density_tags(notes, bar_duration)

def get_density_value(density):
    """From density in notes per quarters returns a density string in
    [LOWEST, LOWER, LOW, MEDIUM, MEDIUM_LOW HIGH, VERY_HIGH]
    :return:

    Parameters
    ----------
    density :
        

    Returns
    -------

    """
    if density < 0.34:
        return "LOWEST"
    if density < 0.5:
        return "LOWER"
    elif density < 2:
        return "LOW"
    elif density < 4:
        return "MEDIUM_LOW"
    elif density < 6:
        return "MEDIUM"
    elif density < 8:
        return "HIGH"
    else:
        return "VERY_HIGH"




def get_density(notes, bar_duration):
    """

    Parameters
    ----------
    notes :
        
    bar_duration :
        

    Returns
    -------

    """

    starts = [start for start, end in notes]
    if not starts:
        return "LOWEST"
    density = len(notes) / bar_duration
    return get_density_value(density)


def get_density_tags(notes, bar_duration):
    """

    Parameters
    ----------
    notes :
        
    bar_duration :
        

    Returns
    -------

    """
    density = get_density(notes, bar_duration)
    return ["CONTROL_DENSITY__" + density]


