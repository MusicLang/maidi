
def get_density_value(density):
    """
    From density in notes per quarters returns a density string in
    [LOWEST, LOWER, LOW, MEDIUM, MEDIUM_LOW HIGH, VERY_HIGH]
    :return:
    """
    if density < 0.34:
        return 'LOWEST'
    if density < 0.5:
        return 'LOWER'
    elif density < 2:
        return 'LOW'
    elif density < 4:
        return 'MEDIUM_LOW'
    elif density < 6:
        return 'MEDIUM'
    elif density < 8:
        return 'HIGH'
    else:
        return 'VERY_HIGH'


def get_token_names():
    return ['CONTROL_DENSITY__' + density for density in ['LOWEST', 'LOWER', 'LOW', 'MEDIUM_LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']]


def get_density(notes, bar_duration):

    starts = [start for start, end in notes]
    if not starts:
        return 'LOWEST'
    density = len(notes) / bar_duration
    return get_density_value(density)


def get_density_tokens(notes, bar_duration):
    density = get_density(notes, bar_duration)
    return ['CONTROL_DENSITY__' + density]
