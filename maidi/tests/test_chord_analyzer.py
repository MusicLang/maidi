import pytest
from maidi.chords.chord_analyzer.chord_analyzer import split_by_tonality, parse_chord_dict, parse_chord, parse_roman_numeral_notation, split_extension_and_added_notes

example_harmonic_progression = """
C: #iv6 ii%6 V6/V Ger6 N V[add9]/ii ii64 V7 I 
c: i vii%7 iio d#: V VI bVII iii65 i(sus2) Fr65
"""


def test_split_by_tonality():
    expected_output = [
        ('#iv6', 'C:'), ('ii%6', 'C:'), ('V6/V', 'C:'), ('Ger6', 'C:'), ('N', 'C:'), ('V[add9]/ii', 'C:'),
        ('ii64', 'C:'), ('V7', 'C:'), ('I', 'C:'), ('i', 'c:'), ('vii%7', 'c:'), ('iio', 'c:'),
        ('V', 'd#:'), ('VI', 'd#:'), ('bVII', 'd#:'), ('iii65', 'd#:'), ('i(sus2)', 'd#:'), ('Fr65', 'd#:')
    ]
    assert split_by_tonality(example_harmonic_progression) == expected_output

def test_parse_chord_dict():
    test_cases = [
        ('#iv6', 'C:', {
            'chord_degree': '#iv', 'chord_extension': '6', 'secondary_tonality': None,
            'main_tonality_degree': 0, 'main_tonality_mode': 'M', 'real_tonality_degree': 0,
            'real_tonality_mode': 'M', 'final_extension': '6', 'final_tonality_degree': 6,
            'final_tonality_mode': 'm', 'final_chord_degree': 0
        }),
    ]
    for chord, tonality, expected_output in test_cases:
        assert parse_chord_dict(chord, tonality) == expected_output

def test_parse_chord():
    test_cases = [
        ('#iv6', 'C:', (0, 6, 'm', '6', [])),
        ("I", "Db:", (0, 1, 'M', '', [])),
        ("V7/V", "f#:", (4, 1, 'M', '7', [])),
        ("ii%65", "C:", (1, 0, 'm', '65', [])),
        ("V6(sus2)[add9]/ii", "C:", (4, 2, 'm', '6(sus2)', ['[add9]'])),
        ("N", "c:", (4, 6, 'm', '6', [])),  # Napolitan chord is always in first inversion
        ("Cad", "D:", (0, 2, 'M', '64', []))  # Cadential chord is always in second inversion
    ]
    for chord, tonality, expected_output in test_cases:
        assert parse_chord(chord, tonality) == expected_output

def test_parse_roman_numeral_notation():
    expected_output = [
        (0, 6, 'm', '6', []),  # C: #iv6
        (1, 0, 'm', '6', []),  # C: ii%6
        (4, 7, 'M', '6', []),  # C: V6/V
        (4, 1, 'M', '6', []),  # C: Ger6
        (4, 6, 'm', '6', []),  # C: N
        (4, 2, 'm', '', ['[add9]']),  # C: V[add9]/ii
        (1, 0, 'M', '64', []),  # C: ii64
        (4, 0, 'M', '7', []),  # C: V7
        (0, 0, 'M', '', []),  # C: I
        (0, 0, 'm', '', []),  # c: i
        (6, 0, 'M', '7', []),  # c: vii%7
        (6, 3, 'm', '', []),  # c: iio
        (4, 3, 'm', '', []),  # d#: V
        (5, 3, 'm', '', []),  # d#: VI
        (4, 6, 'M', '', []),  # d#: bVII
        (2, 3, 'M', '65', []),  # d#: iii65
        (0, 3, 'm', '(sus2)', []),  # d#: i(sus2)
        (4, 4, 'M', '65', [])  # d#: Fr65
    ]
    result = parse_roman_numeral_notation(example_harmonic_progression)
    assert result == expected_output

def test_split_extension_and_added_notes():
    test_cases = [
        ('6', ('6', [])),
        ('64', ('64', [])),
        ('7', ('7', [])),
        ('65', ('65', [])),
        ('43', ('43', [])),
        ('2', ('2', [])),
        ('(sus2)', ('(sus2)', [])),
        ('(sus4)', ('(sus4)', [])),
        ('[add9]', ('', ['[add9]'])),
        ('[addb9]', ('', ['[addb9]'])),
        ('[add11]', ('', ['[add11]'])),
        ('[add#11]', ('', ['[add#11]'])),
        ('[add13]', ('', ['[add13]'])),
        ('[addb13]', ('', ['[addb13]'])),
        ('[add#13]', ('', ['[add#13]'])),
        ('[add#9]', ('', ['[add#9]'])),
        ('[9]', ('', ['[9]'])),
        ('[b9]', ('', ['[b9]'])),
        ('[11]', ('', ['[11]'])),
        ('[#11]', ('', ['[#11]'])),
        ('[13]', ('', ['[13]'])),
        ('[b13]', ('', ['[b13]'])),
        ('[#13]', ('', ['[#13]'])),
        ('[#9]', ('', ['[#9]'])),
        ('6(sus2)', ('6(sus2)', [])),
        ('65[add9]', ('65', ['[add9]'])),
    ]
    for extension, expected_output in test_cases:
        assert split_extension_and_added_notes(extension) == expected_output

if __name__ == "__main__":
    pytest.main()