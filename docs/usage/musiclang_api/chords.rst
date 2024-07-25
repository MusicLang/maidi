.. _chords:

Control chord progressions
==========================

MusicLang Models allow you to control the chord progression of a given generation. More precisely
it lets you control both the chord and the scale used for each bar using standard roman numeral notation.
The chord progression is specified as a list of tuple (or None if you want to let the chord unspecified and let the
model choose one).

In MusicLang you don't choose the duration of the chord but you choose what will be the main sounding chord for a
specific bar, so remember that **in MusicLang one bar = one chord**. Of course that does not prevent the model to do quicker harmonic change
if the context allows it to, but chords are notated with this restriction.

Chord structure
----------------

To help you write chord we use the `maidi.chord_symbols` module
A chord will always be specified by a tuple containing the following properties:

- Chord degree (I, II, III, IV, V, VI, VII) in the scale, as in roman numeral notation
- Tonality (The tonality root, for example E)
- Tonality mode (either minor or major)
- Chord extension, once again in roman numeral notation to account for chord inversion

Example of usage
-----------------

Here is a simple example where we impose a I, vi, ii in first inversion (6), V7 on the key of D major for the generation.
We let the last bar unspecified for a total of 5 chords in the generation:

.. doctest::

    >>> import os
    >>> from maidi import MidiScore, instrument
    >>> import maidi.chords_symbols as cs
    >>> from maidi.integrations.api import MusicLangAPI
    >>> MUSICLANG_API_KEY = os.getenv("MUSICLANG_API_KEY")
    >>> score = MidiScore.from_empty(instruments=[instrument.ELECTRIC_PIANO], nb_bars=5, ts=(4, 4), tempo=120)
    >>> mask, tags, chords = score.get_empty_controls(prevent_silence=True)
    >>> mask[:, :] = 1  # Regenerate everything in the score
    >>> chords = [
    ...     (cs.I, cs.D, cs.major, cs._root_position),
    ...     (cs.VI, cs.D, cs.major, ''),  # Triad in root position can also be written as empty string ''
    ...     (cs.II, cs.D, cs.major, cs._6),
    ...     (cs.V, cs.D, cs.major, cs._7),
    ...     None  # Let the model choose the last chord
    ... ]
    >>> api = MusicLangAPI(MUSICLANG_API_KEY, verbose=True)
    >>> predicted_score = api.predict(score, mask, tags=tags, chords=chords, async_mode=False, polling_interval=3)
    >>> predicted_score.write("predicted_score.mid")

With this example, MusicLang will generate a 5 bars piano score with the given chord/scale progression.


Another example using directly roman numeral notation for the chords :

.. doctest::

    >>> from maidi import ChordManager, MusicLangAPI, MidiScore, instrument, Tags, ScoreTagger
    >>> score = MidiScore.from_empty([instrument.FLUTE, instrument.PIANO], 8)
    >>> chords_string = "c: IV/III ii/III VI/iv viio7 III V/III ii% V7"
    >>> chords = ChordManager.from_roman_string(chords_string)
    >>> mask, tags, _ = score.get_empty_controls()
    >>> mask[:, :] = 1
    >>> api = MusicLangAPI(api_url='https://api.dev.musiclang.io', verbose=False)
    >>> predicted_score = api.predict(score,
    ...                              mask,
    ...                              model='control_masking_large',
    ...                              chords=chords,
    ...                              temperature=0.9,
    ...                             )
    >>> predicted_score.write('predicted_score.mid')
