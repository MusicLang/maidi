import numpy as np
from scipy.spatial.distance import cdist

from .chord_inference_utils import (
    TEMPLATES,
    COEFFS,
    CHROMA_VECTORS_MATRIX,
    PITCH_CLASSES_DICT,
    CHORD_TYPE_TO_PITCHES,
    CHORD_TYPES,
    PITCHES_DICT,
    PITCHES_DICT_ROOT,
)

EXTENSION_DICT = {
    (0, 3): "",
    (1, 3): "6",
    (2, 3): "64",
    (0, 4): "7",
    (1, 4): "65",
    (2, 4): "43",
    (3, 4): "2",
}


def max_correlation_index(
    input_matrix, template_matrix, bass_notes, use_first_max=False
):
    """

    Parameters
    ----------
    input_matrix :
        
    template_matrix :
        
    bass_notes :
        
    use_first_max :
         (Default value = False)

    Returns
    -------

    """

    # Add a small bonus to the bass note

    for i, bass_note in enumerate(bass_notes):
        if bass_note is not None:
            input_matrix[i, int(bass_note)] += 0.2

    # Calculate correlations
    correlations = 1 - cdist(input_matrix, template_matrix, "correlation")
    # Multiply the correlations by coefficients
    correlations *= COEFFS

    # Find index of max correlation for each row
    if use_first_max:
        max_corr_indices = np.argmax(correlations, axis=1)
        chord_type = max_corr_indices % len(TEMPLATES)
        chord_root = max_corr_indices // len(TEMPLATES)
        return chord_root, chord_type

    temp_len = len(TEMPLATES)
    max_corr_indicess = [
        (correlations[i] == np.max(correlations[i, :])).nonzero()[0].tolist()
        for i in range(len(correlations))
    ]
    chord_typess = [
        [i // temp_len for i in max_corr_indices]
        for max_corr_indices in max_corr_indicess
    ]
    chord_rootss = [
        [i % temp_len for i in max_corr_indices]
        for max_corr_indices in max_corr_indicess
    ]

    return chord_rootss, chord_typess


def get_chroma_vectors(pitches_bars):
    """

    Parameters
    ----------
    pitches_bars :
        

    Returns
    -------

    """
    # Remove drums
    pitches_class_array = [p % 12 for p in pitches_bars]
    value_counts = [
        np.bincount(pitches_class, minlength=12)
        for pitches_class in pitches_class_array
    ]
    # Get a 12xnb_bars matrix with each row being the indexes of the pitch class
    bar_chroma_vectors = np.asarray(value_counts)
    normalizer = np.sum(bar_chroma_vectors, axis=1)
    normalizer[normalizer == 0] = 1
    bar_chroma_vectors = bar_chroma_vectors / normalizer[:, None]
    return bar_chroma_vectors


def get_bass_note_bar(pitches_bars):
    """Return the bass note of each bar

    Parameters
    ----------
    notes :
        
    bars :
        
    pitches_bars :
        

    Returns
    -------

    
    """

    bass_notes = []
    for pitches in pitches_bars:
        if len(pitches) == 0:
            bass_notes.append(None)
        else:
            min_pitch = np.min(pitches) % 12
            bass_notes.append(min_pitch)
    return bass_notes


def dynamic_programming_for_chord_inference(lists):
    """

    Parameters
    ----------
    lists :
        

    Returns
    -------

    """

    n = len(lists)
    m = max(len(lst) for lst in lists)
    dp = [[float("inf")] * m for _ in range(n)]
    indices = [[0] * m for _ in range(n)]

    for i, s in enumerate(lists[0]):
        dp[0][i] = 0  # No string changes needed at the start

    for i in range(1, n):
        for j in range(len(lists[i])):
            # FIXME : Better cost function to include relative minor/major and key distances
            for k in range(len(lists[i - 1])):
                if (
                    lists[i][j] != lists[i - 1][k]
                ):  # If the strings are different, we need a change
                    cost = 1
                else:
                    cost = 0

                if (
                    dp[i][j] > dp[i - 1][k] + cost
                ):  # If we found a better (smaller) cost, update the dp and indices array
                    dp[i][j] = dp[i - 1][k] + cost
                    indices[i][j] = k

    res = [0] * n
    min_cost, min_index = min(
        (cost, index) for index, cost in enumerate(dp[-1])
    )  # Find the smallest cost in the last row
    res[-1] = min_index  # The last index is the one with the smallest cost

    for i in range(n - 2, -1, -1):  # Backtrack to find the indices for the other lists
        res[i] = indices[i + 1][res[i + 1]]

    return res


def get_pitch_class_set_tonality(tonality_root, tonality_mode):
    """

    Parameters
    ----------
    tonality_root :
        
    tonality_mode :
        

    Returns
    -------

    """
    major_scale = [0, 2, 4, 5, 7, 9, 11]
    minor_scale = [0, 2, 3, 5, 7, 8, 11]

    pitch_classes = major_scale if tonality_mode == "M" else minor_scale
    pitch_classes = [
        (pitch_class + tonality_root) % 12 for pitch_class in pitch_classes
    ]
    return set(pitch_classes)


def get_pitch_tonality_vector(tonality_root, tonality_mode):
    """

    Parameters
    ----------
    tonality_root :
        
    tonality_mode :
        

    Returns
    -------

    """
    tonality = get_pitch_class_set_tonality(tonality_root, tonality_mode)
    pitch_vector = [1.0 * (i in tonality) for i in range(12)]
    return pitch_vector


def optimal_chord_inference(candidates, chord_durations, bass_notes=None, bars=None):
    """List of candidates per bar

    Parameters
    ----------
    candidates :
        
    chord_durations :
        
    bass_notes :
         (Default value = None)
    bars :
         (Default value = None)

    Returns
    -------

    
    """
    candidates_nb = [
        [(c[1] + 3 * (c[2] == "m")) % 12 for c in candidate] for candidate in candidates
    ]

    indexes = dynamic_programming_for_chord_inference(candidates_nb)
    chords_props = [candidates[i][indexes[i]] for i in range(len(indexes))]

    if bars is None:
        bars = [None] * len(chords_props)
    if bass_notes is None:
        bass_notes = [None] * len(chords_props)

    chords = []
    for (
        (roman, tonality_root, tonality_mode, extension),
        chord_duration,
        bass_note,
    ) in zip(chords_props, chord_durations, bass_notes):
        num, den = chord_duration
        chord = (roman, tonality_root, tonality_mode, num, den, extension)

        if bass_note is not None:
            chord = get_chord_extended_from_bass_note(bass_note, chord)
        else:
            chord = (roman, tonality_root, tonality_mode, 0, extension, num, den)
        chords.append(chord)

    # Find chord octave
    return chords


def get_chord_pitch_classes(roman, tonality_root, tonality_mode, num, den, extension):
    """

    Parameters
    ----------
    roman :
        
    tonality_root :
        
    tonality_mode :
        
    num :
        
    den :
        
    extension :
        

    Returns
    -------

    """
    return PITCHES_DICT[(roman, tonality_root, tonality_mode, extension)]


def get_chord_octave(pitch):
    """

    Parameters
    ----------
    pitch :
        

    Returns
    -------

    """
    return -((pitch + 5) // 12)


def get_base_extension_from_inversion(inversion):
    """Get '' or '7' depending of the inversion (3 or 4 notes chords) and bass idx

    Parameters
    ----------
    inversion :
        return:

    Returns
    -------

    """
    three_notes = ["", "6", "64"]
    four_notes = ["7", "65", "43", "2"]
    is_three_notes = inversion in three_notes
    good_candidate_list = three_notes if is_three_notes else four_notes
    inversion_index = good_candidate_list.index(inversion)
    base_extension = "" if is_three_notes else "7"
    return base_extension, inversion_index


def get_octave_from_chord(roman, tonality_root, tonality_mode, extension):
    """Get the octave of the chord to minimize bass distance to central C

    Parameters
    ----------
    roman :
        param tonality_root:
    tonality_mode :
        param extension:
    tonality_root :
        
    extension :
        

    Returns
    -------

    """
    import re

    pattern = r"\([^)]*\)"
    anti_pattern = r"\(.*?\)"
    inversion = re.sub(pattern, "", extension)
    raw_extension = "".join(re.findall(anti_pattern, extension))
    base_extension, inversion_index = get_base_extension_from_inversion(inversion)
    real_extension = base_extension + raw_extension
    chord_pitches_real = PITCHES_DICT_ROOT[
        (roman, tonality_root, tonality_mode, real_extension)
    ]
    chord_octave = get_chord_octave(chord_pitches_real[inversion_index])
    return chord_octave


def get_chord_extended_from_bass_note(bass_note, chord):
    """

    Parameters
    ----------
    bass_note :
        
    chord :
        

    Returns
    -------

    """
    roman, tonality_root, tonality_mode, num, den, extension = chord
    chord_pitches_class = get_chord_pitch_classes(*chord)
    nb_notes = len(chord_pitches_class)

    chord_pitches_real = PITCHES_DICT_ROOT[
        (roman, tonality_root, tonality_mode, extension)
    ]
    if bass_note in chord_pitches_class:
        bass_idx = chord_pitches_class.index(bass_note)
        root_pitch = chord_pitches_real[bass_idx]
        new_extension = EXTENSION_DICT[(bass_idx, nb_notes)]
        real_extension = new_extension + (
            extension[1:] if extension.startswith("7") else extension
        )
    else:
        root_pitch = chord_pitches_real[0]
        real_extension = extension

    chord_octave = get_chord_octave(root_pitch)
    return roman, tonality_root, tonality_mode, chord_octave, real_extension, num, den


def get_nb_bars(tracks):
    """

    Parameters
    ----------
    tracks :
        

    Returns
    -------

    """
    return len(tracks[list(tracks.keys())[0]])


def concatenate_pitches(T):
    """

    Parameters
    ----------
    T :
        

    Returns
    -------

    """
    return np.concatenate(T) if len(T) > 0 else np.array([], dtype=int)


def fast_chord_inference(tracks, chord_durations):
    """Return the chord progression of the song, one chord per bar
    It uses dynamic programming to find the roman numeral chord progression that minimize the number of tonality changes

    Parameters
    ----------

    tracks : dict
        Dictionary of tracks
        
    chord_durations : list
        List of tuples (num, den) with the duration of each chord in quarters

    Returns
    -------
    list
        List of tuples (roman, tonality_root, tonality_mode, chord_octave, extension, time signature num, time signature den) with the chord progression

    """

    nb_bars = get_nb_bars(tracks)
    pitches_bars = [
        concatenate_pitches(
            [
                track_bar[i]["pitch"]
                for (idx, program, is_drum), track_bar in tracks.items()
                if not is_drum
            ]
        )
        for i in range(nb_bars)
    ]
    bar_chroma_vectors = get_chroma_vectors(pitches_bars)
    # Get the lowest note of each bar
    bass_notes = get_bass_note_bar(pitches_bars)
    chord_rootss, chord_typess = max_correlation_index(
        bar_chroma_vectors, CHROMA_VECTORS_MATRIX, bass_notes, use_first_max=False
    )

    candidates = []
    for chord_roots, chord_types, chroma in zip(
        chord_rootss, chord_typess, bar_chroma_vectors
    ):
        all_sub_candidates = []
        for chord_type, chord_root in zip(chord_roots, chord_types):
            # Get the list of roman numeral candidates
            pitches = tuple(
                sorted(
                    [
                        (chord_root + pitch) % 12
                        for pitch in CHORD_TYPE_TO_PITCHES[CHORD_TYPES[chord_type]]
                    ]
                )
            )
            subcandidates = PITCH_CLASSES_DICT[pitches]
            # Filter only maximum correlation candidates
            pitch_vectors = np.asarray(
                [
                    get_pitch_tonality_vector(tonality_root, tonality_mode)
                    for (
                        roman,
                        tonality_root,
                        tonality_mode,
                        extension,
                    ) in subcandidates
                ]
            )
            correlations = np.asarray(
                [np.correlate(chroma, pitch_vector) for pitch_vector in pitch_vectors]
            )
            # Get the list of maximum correlation candidates (there can be several)
            max_correlations = np.where(correlations == correlations.max())[0]
            subcandidates = [subcandidates[i] for i in max_correlations]
            all_sub_candidates += subcandidates

        if len(all_sub_candidates) == 0:
            all_sub_candidates = [(0, 0, "M", "")]
        candidates.append(all_sub_candidates)

    # Choose the candidate chord path that minimize the number of tonality changes
    chords = optimal_chord_inference(candidates, chord_durations, bass_notes=bass_notes)
    return chords
