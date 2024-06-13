.. _extensions:

Continue an existing song
===========================

You can complete a given midi song for the number of bars of your choice by calling the `MusicLangAPI.extend` method.
Of course, this song extension can be prompted with the usual tags and chords.

The prompted song can be of any length you want, and you can complete your song for as long as you want.

Example
---------

Here is a simple example where we continue an existing song for 4 bars, controlling the chords and note density:

.. doctest::

    >>> import os
    >>> from maidi import MidiScore, instrument, midi_library
    >>> from maidi.integrations.api import MusicLangAPI
    >>> from maidi import chords_symbols as cs
    >>> API_URL = os.getenv("API_URL")
    >>> API_KEY = os.getenv("API_KEY")
    >>> nb_bars_extension = 4
    >>> score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
    >>> chords = [
    ...     (cs.I, cs.C, cs.major, cs._root_position),
    ...     (cs.VI, cs.C, cs.major, ''),  # Triad in root position can also be written as empty string ''
    ...     (cs.II, cs.C, cs.major, cs._6),
    ...     (cs.V, cs.C, cs.major, cs._7),
    ... ]
    >>> tags = [[
    ...     ['CONTROL_MIN_POLYPHONY__1', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_DENSITY__LOW']
    ...     for bar_index in range(nb_bars_extension)
    ... ] for track_index in range(score.nb_tracks)]
    >>> api = MusicLangAPI(API_URL, API_KEY, verbose=True)
    >>> predicted_score = api.extend(score, nb_bars_extension, chords=chords, tags=tags, nb_added_bars_step=2, async_mode=False, polling_interval=3)
    >>> predicted_score.write("predicted_score.mid")
