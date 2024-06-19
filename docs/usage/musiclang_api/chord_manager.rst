Chords Notation Guide
=====================

This chapter provides guidelines on how to write chords using the features supported by the chord parser functions. The notation includes tonalities, chord degrees, extensions, and special cases.

Example: Parsing a Chord Progression
------------------------------------

Let's start with an example of parsing a chord progression using the provided functions.

Example Chord Progression::

.. doctest::

    >>> from maidi.analysis.chord_analyzer import parse_roman_numeral_notation
    >>> input_string = "C: #iv6 ii%6 V6/V Ger6 N V[add9]/ii ii64 V7 I c: i vii%7 iio d#: V VI VII iii65 i(sus2) Fr65"
    >>> result = parse_roman_numeral_notation(input_string)


Tonalities
----------

Tonalities are specified using a note followed by a colon. The note can be in uppercase for major tonalities or lowercase for minor tonalities. Sharps (`#`) and flats (`b`) can also be used.

Examples:
    - `C:` for C major
    - `c:` for C minor
    - `d#:` for D# major
    - `gb:` for Gb minor

Chord Degrees
-------------

Chord degrees are specified using Roman numerals. Uppercase Roman numerals represent major chords, while lowercase Roman numerals represent minor chords. Sharps (`#`) and flats (`b`) can also be used.

Examples:
    - `I` for the major tonic chord
    - `ii` for the minor supertonic chord
    - `#iv` for the raised subdominant chord
    - `VII` seventh degree chord (In C major, B major, in c minor, Bb major)

Because maidi derives chord/scales, actual scale is derived from the tonality, chord degree and secondary tonality.

Chord Extensions
----------------

Chord extensions are specified using various symbols and numbers. Common extensions include `7` for seventh chords, `6` for sixth chords, and `sus2` or `sus4` for suspended chords. Extensions can be combined with chord degrees.

Examples:
    - `I7` for a major seventh chord
    - `ii6` for a minor sixth chord
    - `V7` for a dominant seventh chord
    - `iv(sus4)` for a minor suspended fourth chord

Secondary Tonalities
--------------------

Secondary tonalities are specified using a slash (`/`) followed by the secondary chord degree. This indicates that the chord is borrowed from another key.

Examples:
    - `V7/V` for a dominant seventh chord of the dominant
    - `ii%6/ii` for a half-diminished sixth chord of the supertonic

Special Cases
-------------

Certain chords have special notations and rules:

- **Neapolitan Chord (N)**: Always in first inversion.
  Example: `N` in C major is `bII6`.

- **Cadential Chord (Cad)**: Always in second inversion.
  Example: `Cad` in D major is `I64`.

- **German Augmented Sixth (Ger)**, **Italian Augmented Sixth (It)**, and **French Augmented Sixth (Fr)**: These chords have specific notations from classical and romantic music.
  Examples:
    - `Ger6` in C major
    - `It6` in C major
    - `Fr6` in C major

Examples
--------

Here are some examples of complete chord progressions with their tonalities:

1. `C: #iv6 ii%6 V6/V Ger6 N V[add9]/ii ii64 V7 I`
2. `c: i vii%7 iio`
3. `d#: V VI VII iii65 i(sus2) Fr65`

Each chord is associated with its primary tonality, and the parser functions will correctly interpret the degrees, extensions, and special cases.

Usage
-----

To use these notations in your code, simply pass the input string containing the chords and tonalities to the parser functions. The functions will return the parsed properties of each chord.

Example::

    input_string = "C: #iv6 ii%6 V6/V Ger6 N V[add9]/ii ii64 V7 I c: i vii%7 iio d#: V VI VII iii65 i(sus2) Fr65"
    result = parse_roman_numeral_notation(input_string)
    print(result)

This will output a list of tuples containing the parsed properties of each chord.

By following these guidelines, you can write chords that are compatible with the chord parser functions and take advantage of their full range of features.