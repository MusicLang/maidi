.. _from_scratch:

Generate an idea from scratch
==============================

With the `generate_from_scratch` method of the MusicLang API you can create an idea from 1 to 16 bars with
the instruments, time signature, tempo of your choice. You can even customize the chords and the musical properties of each bars
with the `chords` and `tags` parameters.

Example
--------

Here is an example of how to generate a 4 bars drum and bass idea with the MusicLang API:

.. doctest::

    >>> from maidi import MidiScore
    >>> from maidi import instrument
    >>> from maidi.integrations.api import MusicLangAPI
    >>> import os
    >>> api = MusicLangAPI(api_key=os.getenv("MUSICLANG_API_KEY"), verbose=True)
    >>> instruments = [instrument.DRUMS, instrument.ELECTRIC_BASS_FINGER]
    >>> nb_bars = 4
    >>> time_signature = (4, 4)
    >>> tempo = 120
    >>> predicted_score = api.generate_from_scratch(instruments=instruments, nb_bars=nb_bars, ts=time_signature, tempo=tempo)
    >>> predicted_score.write("predicted_score.mid")
