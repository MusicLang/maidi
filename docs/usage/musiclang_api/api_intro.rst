.. _general_usage:

Introduction
====================

MusicLang is your **co-pilot for music composition**.

Based on generative AI technology and trained on CC0 midi music data.

Using this package you get an **easy python integration with MusicLang** for your music tech projects.

Learn more about musiclang `here <https://www.musiclang.io>`_.


Documentation
--------------------------

:ref:`models`

:ref:`from_scratch`

:ref:`chords`

:ref:`tags`

:ref:`extensions`

:ref:`transitions`


Official API documentation
---------------------------

While this package provides a simple interface to the MusicLang API, you can also use the API directly :

`Read more here <http://api.musiclang.io/documentation>`_


Examples
----------

Here are some basic examples of how you can use the MusicLang API to leverage the power of the musiclang model.

**1. Generate a 4 bar score with the musiclang masking model API**.

Just set your API_URL and MUSICLANG_API_KEY in the environment (or get one `here <https://www.musiclang.io>`_) and run the following code:

.. doctest::

    >>> import os
    >>> MUSICLANG_API_KEY = os.getenv("MUSICLANG_API_KEY")
    >>> from maidi.integrations.api import MusicLangAPI
    >>> from maidi import MidiScore, instrument
    >>> import numpy as np
    >>> api = MusicLangAPI(MUSICLANG_API_KEY)
    >>> score = MidiScore.from_empty(instruments=[instrument.PIANO, instrument.ELECTRIC_BASS_FINGER], nb_bars=4, ts=(4, 4), tempo=120)
    >>> mask = np.ones((2, 4))
    >>> predicted_score = api.predict(score, mask, model="control_masking_large", timeout=120, temperature=0.95)

**2. Generate a new track in a score**: Start from a midi file and add a track:

.. doctest::

    >>> import os
    >>> MUSICLANG_API_KEY = os.getenv("MUSICLANG_API_KEY")
    >>> from maidi import MidiScore, instrument, midi_library
    >>> from maidi.integrations.api import MusicLangAPI
    >>> score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
    >>> score = score.add_instrument(instrument.CLEAN_GUITAR)
    >>> mask, _, _ = score.get_empty_controls(prevent_silence=True)
    >>> mask[-1, :] = 1  # Generate the last track
    >>> api = MusicLangAPI(MUSICLANG_API_KEY, verbose=True)
    >>> predicted_score = api.predict(score, mask, async_mode=False, polling_interval=3)
    >>> predicted_score.write("predicted_score.mid")

**3. Generate a song that has the same characteristics as an existing midi file**: Start from a midi file and generate a new track with the same characteristics:

.. doctest::

    >>> import os
    >>> MUSICLANG_API_KEY = os.getenv("MUSICLANG_API_KEY")
    >>> from maidi import MidiScore, ScoreTagger, midi_library
    >>> from maidi.analysis import tags_providers
    >>> from maidi.integrations.api import MusicLangAPI
    >>> score = MidiScore.from_midi(midi_library.get_midi_file('example1'))
    >>> score = score[0, :4]
    >>> tagger = ScoreTagger([
    ...     tags_providers.DensityTagsProvider(),
    ...     tags_providers.MinMaxPolyphonyTagsProvider(),
    ...     tags_providers.MinMaxRegisterTagsProvider(),
    ...     tags_providers.SpecialNotesTagsProvider(),
    ... ])
    >>> tags = tagger.tag_score(score)
    >>> chords = score.get_chords_prompt()
    >>> mask = score.get_mask()
    >>> mask[:, :] = 1  # Regenerate everything in the score
    >>> api = MusicLangAPI(MUSICLANG_API_KEY, verbose=True)
    >>> predicted_score = api.predict(score, mask, async_mode=False, polling_interval=3)
    >>> predicted_score.write("predicted_score.mid")

For more details on the API, please refer to the `MusicLang API documentation <https://api.musiclang.io/documentation>`_ .

:ref:`back to top <integrations>`
