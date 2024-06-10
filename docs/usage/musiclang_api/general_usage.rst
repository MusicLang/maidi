.. _general_usage:


General usage
===========================



Examples
----------


Here are some basic example on how you can use MusicLang API to leverage the power of the musiclang model.

**1. Generate a 4 bar score** with the musiclang masking model API.
Just set your API_URL and API_KEY in the environment (or get one `here <https://www.musiclang.io>`_) and run the following code ::

    from maidi import MidiScore
    from maidi import instrument
    import os
    from maidi.integrations.api import MusicLangAPI

    # Assuming API_URL and API_KEY are set in the environment
    API_URL = os.getenv("API_URL")
    API_KEY = os.getenv("API_KEY")

    # Your choice of params for generation here
    instruments = [
        instrument.DRUMS,
        instrument.ELECTRIC_BASS_FINGER,
    ]

    # Create a 4 bar template with the given instruments
    score = MidiScore.from_empty(
        instruments=instruments, nb_bars=4, ts=(4, 4), tempo=120
    )
    # Get the controls (the prompt) for this score
    mask, tags, chords = score.get_empty_controls(prevent_silence=True)
    mask[:, :] = 1  # Regenerate everything in the score

    # Call the musiclang API to predict the score
    api = MusicLangAPI(API_URL, API_KEY, verbose=True)
    predicted_score = api.predict(score,
        mask, tags=tags, chords=chords, async_mode=False, polling_interval=5
    )
    predicted_score.write("predicted_score.mid")


**2. Generate a new track in a score** : Start from a midi file and add a track ::


    import os
    from maidi import MidiScore, instrument, midi_library
    from maidi.integrations.api import MusicLangAPI

    # Assuming API_URL and API_KEY are set in the environment
    API_URL = os.getenv("API_URL")
    API_KEY = os.getenv("API_KEY")

    # Create a 4 bar template with the given instruments
    score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
    # Add a clean guitar track and set the mask
    score = score.add_instrument(instrument.CLEAN_GUITAR)
    mask, _, _ = score.get_empty_controls(prevent_silence=True)
    mask[-1, :] = 1  # Generate the last track

    # Call the musiclang API to predict the score
    api = MusicLangAPI(API_URL, API_KEY, verbose=True)
    predicted_score = api.predict(score,
        mask, async_mode=False, polling_interval=3
    )
    predicted_score.write("predicted_score.mid")


**3. Generate a song that has the same characteristics as an existing midi files** : Start from a midi file and generate a new track with the same characteristics. ::

    import os
    from maidi import MidiScore, ScoreTagger, midi_library
    from maidi.analysis import tags_providers
    from maidi.integrations.api import MusicLangAPI

    # Assuming API_URL and API_KEY are set in the environment
    API_URL = os.getenv("API_URL")
    API_KEY = os.getenv("API_KEY")
    # Load a midi file
    score = MidiScore.from_midi(midi_library.get_midi_file('example1'))

    # Get a score with the first track and the first 4 bars of the midi file
    score = score[0, :4]

    tagger = ScoreTagger(
        [
            tags_providers.DensityTagsProvider(),
            tags_providers.MinMaxPolyphonyTagsProvider(),
            tags_providers.MinMaxRegisterTagsProvider(),
            tags_providers.SpecialNotesTagsProvider(),
        ]
    )
    tags = tagger.tag_score(score)
    chords = score.get_chords_prompt()
    mask = score.get_mask()
    mask[:, :] = 1  # Regenerate everything in the score

    api = MusicLangAPI(API_URL, API_KEY, verbose=True)
    predicted_score = api.predict(score,
        mask, async_mode=False, polling_interval=3
    )
    predicted_score.write("predicted_score.mid")


For more details on the API, please refer to the `MusicLang API documentation <https://api.musiclang.io/documentation>`_ .

:ref:`back to top <integrations>`
