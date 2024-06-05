from maidi.analysis import TagsProvider

REGISTERS = {
    "highest": (81, 130),
    "sopranissimo": (74, 95),
    "soprano": (60, 81),
    "mezzo_soprano": (57, 78),
    "alto": (55, 76),
    "contralto": (53, 74),
    "tenor": (48, 69),
    "baritone": (45, 65),
    "bass": (41, 64),
    "contrabass": (36, 57),
    "lowest": (0, 36),
}

ORDERED_FROM_LOWEST = list(
    sorted(REGISTERS.keys(), key=lambda x: REGISTERS[x][0], reverse=True)
)
ORDERED_FROM_HIGHEST = list(sorted(REGISTERS.keys(), key=lambda x: REGISTERS[x][1]))

LOW_PITCHES = [REGISTERS[x][0] for x in ORDERED_FROM_LOWEST]






def get_tags_names():
    """

    Returns
    -------

    """
    min_tokens = [
        "CONTROL_MIN_REGISTER__" + register for register in ORDERED_FROM_LOWEST
    ]
    max_tokens = [
        "CONTROL_MAX_REGISTER__" + register for register in ORDERED_FROM_HIGHEST
    ]
    return min_tokens + max_tokens


class MinMaxRegisterTagsProvider(TagsProvider):
    ALL_TAGS = get_tags_names()

    def get_tags(self, track_bar, chord, score):
        pitches = self.get_pitches(track_bar, chord, score)
        return get_min_max_register_tags(pitches)



def get_min_max_registers(pitches: list[int]) -> list[str]:
    """Get highest register that encompasses min_pitch, and lowest register that encompasses max_pitch

    Parameters
    ----------
    pitches :
        List of pitch values
    pitches: list[int] :
        

    Returns
    -------
    type
        Tuple containing the highest and lowest registers

    """
    pitches = set(pitches)
    if len(pitches) == 0:
        return []

    min_pitch = min(pitches)
    max_pitch = max(pitches)

    min_register = "tenor"  # Assuming this is the lowest register
    max_register = "tenor"  # Assuming this is the highest register

    for register in ORDERED_FROM_LOWEST:
        if REGISTERS[register][0] <= min_pitch:
            min_register = register
            break

    if max_pitch <= REGISTERS[min_register][1]:
        return [min_register, min_register]

    for register in ORDERED_FROM_HIGHEST:
        if REGISTERS[register][1] >= max_pitch:
            max_register = register
            break

    return [min_register, max_register]


def get_min_max_register_tags(pitches: list[int]) -> list[str]:
    """

    Parameters
    ----------
    pitches: list[int] :


    Returns
    -------

    """
    registers = get_min_max_registers(pitches)
    if len(registers) == 0:
        return []
    return [
        "CONTROL_MIN_REGISTER__" + registers[0],
        "CONTROL_MAX_REGISTER__" + registers[1],
    ]


def get_token_names():
    """ """
    min_tokens = [
        "CONTROL_MIN_REGISTER__" + register for register in ORDERED_FROM_LOWEST
    ]
    max_tokens = [
        "CONTROL_MAX_REGISTER__" + register for register in ORDERED_FROM_HIGHEST
    ]
    return min_tokens + max_tokens
