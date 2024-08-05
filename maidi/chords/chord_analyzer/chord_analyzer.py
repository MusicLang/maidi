import re
import itertools

VALID_EXTENSIONS_ = {'6', '64', '7', '65', '43', '2', ''}
VALID_SUS = {'', '(sus2)', '(sus4)'}
VALID_EXTENSIONS = set([a + b for a, b in itertools.product(VALID_EXTENSIONS_, VALID_SUS)])
VALID_ADDED_NOTES = {'[add9]', '[addb9]', '[add11]', '[add#11]', '[add13]', '[addb13]', '[add#13]', '[add#9]', '[9]', '[b9]', '[11]',
                     '[#11]', '[13]', '[b13]', '[#13]', '[#9]'}


CHORD_REGEX = re.compile(r"^(Ger|Cad|Fr|It|N|[#b]*[ivIV]+[o%ø+]?)(6|64|7|65|43|2)?(\(sus2\)|\(sus4\))?(\[add9\]|\[addb9\]|\[add11\]|\[add#11\]|\[add13\]|\[addb13\]|\[add#10\]|\[add#13\]|\[add#9\]|\[9\]|\[b9\]|\[11\]|\[#11\]|\[13\]|\[b13\]|\[#13\|\[#10\]])?(/[#b]*[ivIV]+)?$")
CHORD_PROGRESSION_REGEX = re.compile(r"(x\s*)?([A-Ga-g][#b]?:\s*)?((x|Ger|Cad|Fr|It|N|[#b]*[ivIV]+[o%ø+]?)(6|64|7|65|43|2)?(\(sus2\)|\(sus4\))?(\[add9\]|\[addb9\]|\[add11\]|\[add#11\]|\[add13\]|\[addb13\]|\[add#10\]|\[add#13\]|\[add#9\]|\[9\]|\[b9\]|\[11\]|\[#11\]|\[13\]|\[b13\]|\[#13\|\[#10\])?(/[#b]*[ivIV]+)?\s*)+")

def split_by_tonality(input_string):
    """
    Splits the input string by tonalities and associates each chord with its primary tonality.

    Args:
        input_string (str): The input string containing chords with tonalities.

    Returns:
        List[Tuple[str, str]]: A list of tuples where each tuple contains a chord and its associated primary tonality.
    """
    input_string = " ".join(input_string.split())
    # Regular expression to match tonalities (e.g., C:, c:, d#:)
    tonality_pattern = re.compile(r'([A-Ga-g][#b]?:)')

    # Find all tonalities in the input string
    tonalities = tonality_pattern.findall(input_string)
    if not tonalities:
        raise ValueError("No tonalities found in the input string.")

    # Split the input string by tonalities
    segments = tonality_pattern.split(input_string)

    # Remove empty strings from segments
    segments = [seg for seg in segments if seg]

    if len(segments) % 2 != 0:
        raise ValueError("Malformed input string. Tonalities and chords are not properly paired.")

    # Pair each chord segment with its associated tonality
    result = []
    for i in range(0, len(segments), 2):
        tonality = segments[i]
        chords = segments[i + 1].strip().split()
        for chord in chords:
            result.append((chord, tonality))

    return result


TONALITIES_DICT = {
    "c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11
}


def tonality_name_to_degree(main_tonality_degree):
    main_tonality_degree = main_tonality_degree.lower()
    main_tonality_note_degree = TONALITIES_DICT[main_tonality_degree[0]]

    # Count the number of sharps in tonality
    nb_sharps = re.findall("#", main_tonality_degree[1:])
    nb_sharps = len(nb_sharps)

    # Count the number of flats in tonality
    nb_flats = re.findall("b", main_tonality_degree[1:])
    nb_flats = len(nb_flats)

    # Determine the tonality degree modified with flats and sharps
    main_tonality_note_degree = (main_tonality_note_degree + nb_sharps - nb_flats) % 12

    return main_tonality_note_degree


def parse_special_cases(chord_result):
    chord_degree = chord_result['chord_degree']
    chord_extension = chord_result['chord_extension']

    if chord_degree == 'N' and chord_extension == '':
        chord_result['chord_extension'] = '6'
        chord_result['final_extension'] = '6'

    if chord_degree == 'Cad' and chord_extension == '':
        chord_result['chord_extension'] = '64'
        chord_result['final_extension'] = '64'

    return chord_result


def parse_chord_dict(chord, tonality):
    """
    Parses a chord and extracts the desired properties.

    Args:
        chord (str): The chord to be parsed.
        tonality (str): The primary tonality associated with the chord.

    Returns:
        Dict[str, str]: A dictionary containing the parsed properties of the chord.
    """
    # Regular expressions for different parts of the chord
    degree_pattern = re.compile(r'^(Ger|Cad|Fr|It|N|(#|b)*[ivIV]+)')
    secondary_tonality_pattern = re.compile(r'/((#|b)*[ivIV]+)')

    # Extract chord degree
    degree_match = degree_pattern.match(chord)
    if not degree_match:
        raise ValueError(f"Invalid chord degree in chord: {chord}")
    chord_degree = degree_match.group(0)

    # Extract chord extension
    extension_match = chord.split('/')[0]
    chord_extension = extension_match[len(chord_degree):]

    # Extract secondary tonality
    secondary_tonality_match = secondary_tonality_pattern.search(chord)
    secondary_tonality = secondary_tonality_match.group(1) if secondary_tonality_match else None

    # Determine main tonality degree and mode
    main_tonality_degree = tonality[:-1]  # Remove the colon
    main_tonality_degree = tonality_name_to_degree(main_tonality_degree)
    main_tonality_mode = "m" if tonality[0].islower() else "M"

    result = {
        "chord_degree": chord_degree,
        "chord_extension": chord_extension,
        "secondary_tonality": secondary_tonality,
        "main_tonality_degree": main_tonality_degree,
        "main_tonality_mode": main_tonality_mode
    }

    from maidi.chords.chord_analyzer.chord_constants import DICT_TONALITY, DICT_RELATIVE_CHANGE

    # Determine the actual tonality degree if secondary tonality
    if secondary_tonality:
        tonality_degree, tonality_mode = DICT_TONALITY[main_tonality_mode][secondary_tonality]
        result["real_tonality_degree"] = (tonality_degree + main_tonality_degree) % 12
        result["real_tonality_mode"] = tonality_mode
    else:
        result["real_tonality_degree"] = main_tonality_degree
        result["real_tonality_mode"] = main_tonality_mode

    # Get the extension only if "o" or "%" or "ø" or "+" is present
    chord_extension_found = re.search(r'[o%ø+]', chord_extension)
    chord_extension_found = chord_extension_found.group(0) if chord_extension_found else ""

    # Remove chord extension found from extension
    result['final_extension'] = result['chord_extension'].replace(chord_extension_found, "")

    total_degree = chord_degree + chord_extension_found
    total_degree = total_degree.replace('%', 'ø')

    # Determine the relative change (0, 'M', 0), Degree, mode, offset tonality
    real_tonality_mode = result['real_tonality_mode']
    degree, final_mode, offset_tonality = DICT_RELATIVE_CHANGE[real_tonality_mode][total_degree]
    result['final_tonality_degree'] = (result['real_tonality_degree'] + offset_tonality) % 12
    result['final_tonality_mode'] = final_mode
    result['final_chord_degree'] = degree

    result = parse_special_cases(result)

    return result


def parse_chord(chord, tonality):
    """
    Parses a chord and extracts the desired properties.

    Args:
        chord (str): The chord to be parsed.
        tonality (str): The primary tonality associated with the chord.

    Returns:
        Tuple: A tuple containing the parsed properties of the chord.
    """
    # Check valid chord
    if chord == 'x':
        return None
    if not CHORD_REGEX.match(chord):
        raise ValueError(f"Invalid chord: {chord}")

    try:
        result = parse_chord_dict(chord, tonality)
        degree = result['final_chord_degree']
        tonality = result['final_tonality_degree']
        mode = result['final_tonality_mode']
        extension = result['final_extension']

        # Split the extension and added notes
        final_roman_extension, final_added_notes = split_extension_and_added_notes(extension)

        return degree, tonality, mode, final_roman_extension, final_added_notes
    except ValueError as e:
        raise ValueError(f"Error parsing chord: {e}")



def split_extension_and_added_notes(extension):
    """
    Splits the extension into roman extension and added notes.

    Args:
        extension (str): The chord extension.

    Returns:
        Tuple[str, List[str]]: A tuple containing the roman extension and a list of added notes.
    """

    remove_roman_extension = False

    # Split the extension by parentheses
    parts = re.split(r'(\[.*?\])', extension)

    final_roman_extension = ""
    final_added_notes = []

    for part in parts:
        # This is the main extension part
        if part in VALID_EXTENSIONS:
            final_roman_extension += part
        elif part == "":
            # Handle the case where the roman numeral extension is an empty string
            continue
        else:
            # Check if the part is an added note without parentheses
            if part in VALID_ADDED_NOTES:
                final_added_notes.append(part)
            else:
                raise ValueError(f"Invalid roman extension: {part}")

    if remove_roman_extension:
        final_roman_extension = ""

    return final_roman_extension, final_added_notes
def parse_roman_numeral_notation(input_string):
    """
    Parses a Roman numeral notated string and extracts the desired properties for each chord.

    Args:
        input_string (str): The input string containing chords with tonalities.

    Returns:
        List[Dict[str, str]]: A list of dictionaries where each dictionary contains the parsed properties of a chord.
    """
    # Check chord progression regex
    input_string = " ".join(input_string.split())
    if not CHORD_PROGRESSION_REGEX.match(input_string):
        raise ValueError(f"Invalid chord progression: {input_string}")

    try:
        # Split the input string by tonalities
        chords_with_tonalities = split_by_tonality(input_string)

        # Parse each chord and extract properties
        parsed_chords = []
        for chord, tonality in chords_with_tonalities:
            parsed_chord = parse_chord(chord, tonality)
            parsed_chords.append(parsed_chord)

        return parsed_chords
    except ValueError as e:
        raise ValueError(f"Error parsing input string: {e}")