from maidi.chords.chord_inference_utils import SCALES


def to_pitch(type, idx, oct, chord):
    """
    Return the pitch from the note type, idx, octave and chord

    Parameters
    ----------
    type : str
        
    idx : int
        
    oct : int
        
    chord : tuple
        

    Returns
    -------

    """
    (
        roman,  #  Chord degree 0-indexed
        tonality_root,
        tonality_mode,
        chord_octave,
        real_extension,
        num,
        den,
    ) = chord
    base_scale = SCALES[tonality_mode]
    base_scale = (
        [base_scale[roman]]
        + base_scale[roman + 1 :]
        + [a + 12 for a in base_scale[:roman]]
    )
    scale = [s + tonality_root + 12 * chord_octave for s in base_scale]
    chromatic_scale = [
        s + base_scale[0] + tonality_root + 12 * chord_octave for s in range(12)
    ]
    if type == "s":
        scale = scale
    elif type == "d":
        return 60 + idx + 12 * oct
    elif type == "a":
        return 60 + idx + 12 * oct
    else:
        scale = chromatic_scale
    return 60 + scale[idx] + 12 * oct


def pitch_to_note_type(pitch, velocity, time, duration, chord, is_drum, is_absolute):
    """

    Parameters
    ----------
    pitch :
        
    velocity :
        
    time :
        
    duration :
        
    chord :
        
    is_drum :
        
    is_absolute :
        

    Returns
    -------

    """
    (
        roman,
        tonality_root,
        tonality_mode,
        chord_octave,
        real_extension,
        num,
        den,
        chord_start,
        chord_end,
    ) = chord
    type, idx, oct = parse_pitch(pitch, chord, is_drum, is_absolute)
    amp = get_amp_figure(velocity)
    time = int(time)  # Previously : - chord_start
    duration = int(duration)

    return type, idx, oct, amp, time, duration


def get_amp_figure(velocity):
    """

    Parameters
    ----------
    velocity :
        

    Returns
    -------

    """
    n = velocity / 120
    if n is None or n <= 0:
        return "n"
    elif n <= 0.16:
        return "ppp"
    elif n <= 0.26:
        return "pp"
    elif n <= 0.36:
        return "p"
    elif n <= 0.5:
        return "mp"
    elif n <= 0.65:
        return "mf"
    elif n <= 0.8:
        return "f"
    elif n <= 0.9:
        return "ff"
    else:
        return "fff"


def amp_figure_to_velocity(amp_figure):
    """

    Parameters
    ----------
    amp_figure :
        

    Returns
    -------

    """
    if amp_figure == "n":
        return 0
    elif amp_figure == "ppp":
        return int(120 * 0.16)
    elif amp_figure == "pp":
        return int(120 * 0.26)
    elif amp_figure == "p":
        return int(120 * 0.36)
    elif amp_figure == "mp":
        return int(120 * 0.5)
    elif amp_figure == "mf":
        return int(120 * 0.65)
    elif amp_figure == "f":
        return int(120 * 0.8)
    elif amp_figure == "ff":
        return int(120 * 0.9)
    else:
        return int(120 * 0.95)


def parse_pitch(pitch, chord, is_drum, is_absolute):
    """Parse an integer pitch (0=C5)

    Parameters
    ----------
    pitch :
        
    chord :
        
    is_drum :
        
    is_absolute :
        

    Returns
    -------

    
    """
    (
        roman,
        tonality_root,
        tonality_mode,
        chord_octave,
        real_extension,
        num,
        den,
    ) = chord
    pitch = pitch - 60  # C5
    if is_drum:
        return "d", pitch % 12, pitch // 12
    if is_absolute:
        return "a", pitch % 12, pitch // 12

    base_scale = SCALES[tonality_mode]
    base_scale = (
        [base_scale[roman]]
        + base_scale[roman + 1 :]
        + [a + 12 for a in base_scale[:roman]]
    )
    scale = [s + tonality_root + 12 * chord_octave for s in base_scale]
    scale_class = [s % 12 for s in scale]
    chromatic_scale = [
        s + base_scale[0] + tonality_root + 12 * chord_octave for s in range(12)
    ]
    scale_class_set = set(scale_class)
    if pitch % 12 in scale_class_set:
        scale = scale
        type = "s"
    else:
        scale = chromatic_scale
        type = "h"

    scale_mod = [s % 12 for s in scale]
    idx = scale_mod.index(pitch % 12)
    oct = (pitch - scale[0]) // 12

    return type, idx, oct
