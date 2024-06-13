.. _transitions:

Generate transitions
========================

You have composed two parts and you want to generate a transition between them?
This is a common use case in music composition that can sometimes be a little bit technical.
We provide a simple way to generate transitions between two parts using the `create_transition` method of the API wrapper.

Example
--------

Here is an example of how to generate transitions between two parts (here we chose the same 4 bars):

.. doctest::

    >>> import os
    >>> from maidi import MidiScore, midi_library
    >>> from maidi.integrations.api import MusicLangAPI
    >>> API_URL = os.getenv("API_URL")
    >>> API_KEY = os.getenv("API_KEY")
    >>> nb_bars_transition = 4  # Should be less than 12 bars, the higher the value the less context is added to the model
    >>> score1 = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
    >>> score2 = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
    >>> api = MusicLangAPI(API_URL, API_KEY, verbose=True)
    >>> predicted_score = api.create_transition(score1, score2, nb_bars_transition, async_mode=False, polling_interval=3)
    >>> predicted_score.write("predicted_score.mid")
