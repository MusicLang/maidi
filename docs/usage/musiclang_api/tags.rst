.. _tags:


Control other musical elements
==================================

The MusicLang model is controlled by a set of tags that can be used to guide the generation of the music. The tags are
used to control for example the density of notes, the number of voices playing at the same time, the pitch register, specific notes that should be used in the
generated music.

- You control the tags at the bar/track level. So you can have different tags (or not at all) for each bar and each track.
- The tags are used to guide the model to generate music that is more likely to be similar to the tags.
- You can tag a given score using this package and use the tags as a prompt for the model to generate music that looks alike the tagged score.


List of possible tags
----------------------

Here is a list of possible tags in the current version of the model. The tags are divided into 4 categories: **Density**, **Polyphony**, **Register** and **Special Notes**.
You can control the tags at the level of each bar of each track.

- **CONTROL_DENSITY__HIGH:** Density of notes is HIGH, with a rate of 6 to 8 notes per quarter.
- **CONTROL_DENSITY__LOW:** Density of notes is LOW, with a rate of 0.5 to 2 notes per quarter.
- **CONTROL_DENSITY__LOWER:** Density of notes is LOWER, with a rate of 0.34 to 0.5 notes per quarter.
- **CONTROL_DENSITY__LOWEST:** Density of notes is the LOWEST, with a rate of less than 0.34 notes per quarter.
- **CONTROL_DENSITY__MEDIUM:** Density of notes is MEDIUM, with a rate of 4 to 6 notes per quarter.
- **CONTROL_DENSITY__MEDIUM_LOW:** Density of notes is MEDIUM_LOW, with a rate of 2 to 4 notes per quarter.
- **CONTROL_DENSITY__VERY_HIGH:** Density of notes is VERY_HIGH, with a rate of more than 8 notes per quarter.
- **CONTROL_MAX_POLYPHONY__0:** Maximum polyphony is 0 notes (silenced bar).
- **CONTROL_MAX_POLYPHONY__1:** Maximum polyphony is 1 note. (monophonic)
- **CONTROL_MAX_POLYPHONY__2:** Maximum polyphony is 2 notes.
- **CONTROL_MAX_POLYPHONY__3:** Maximum polyphony is 3 notes.
- **CONTROL_MAX_POLYPHONY__4:** Maximum polyphony is 4 notes.
- **CONTROL_MAX_POLYPHONY__5:** Maximum polyphony is 5 notes.
- **CONTROL_MAX_POLYPHONY__6:** Maximum polyphony is 6 notes.
- **CONTROL_MIN_POLYPHONY__0:** Minimum polyphony is 0 notes (silenced bar).
- **CONTROL_MIN_POLYPHONY__1:** Minimum polyphony is 1 note. (monophonic)
- **CONTROL_MIN_POLYPHONY__2:** Minimum polyphony is 2 notes.
- **CONTROL_MIN_POLYPHONY__3:** Minimum polyphony is 3 notes.
- **CONTROL_MIN_POLYPHONY__4:** Minimum polyphony is 4 notes.
- **CONTROL_MIN_POLYPHONY__5:** Minimum polyphony is 5 notes.
- **CONTROL_MIN_POLYPHONY__6:** Minimum polyphony is 6 notes.
- **CONTROL_MAX_REGISTER__lowest:** Maximum register is LOWEST (pitch range: 0 to 36).
- **CONTROL_MAX_REGISTER__contrabass:** Maximum register is CONTRABASS (pitch range: 36 to 57).
- **CONTROL_MAX_REGISTER__bass:** Maximum register is BASS (pitch range: 41 to 64).
- **CONTROL_MAX_REGISTER__baritone:** Maximum register is BARITONE (pitch range: 45 to 65).
- **CONTROL_MAX_REGISTER__alto:** Maximum register is ALTO (pitch range: 55 to 76).
- **CONTROL_MAX_REGISTER__contralto:** Maximum register is CONTRALTO (pitch range: 53 to 74).
- **CONTROL_MAX_REGISTER__tenor:** Maximum register is TENOR (pitch range: 48 to 69).
- **CONTROL_MAX_REGISTER__mezzo_soprano:** Maximum register is MEZZO_SOPRANO (pitch range: 57 to 78).
- **CONTROL_MAX_REGISTER__soprano:** Maximum register is SOPRANO (pitch range: 60 to 81).
- **CONTROL_MAX_REGISTER__sopranissimo:** Maximum register is SOPRANISSIMO (pitch range: 74 to 95).
- **CONTROL_MAX_REGISTER__highest:** Maximum register is HIGHEST (pitch range: 81 to 130).
- **CONTROL_MIN_REGISTER__lowest:** Minimum register is LOWEST (pitch range: 0 to 36).
- **CONTROL_MIN_REGISTER__contrabass:** Minimum register is CONTRABASS (pitch range: 36 to 57).
- **CONTROL_MIN_REGISTER__bass:** Minimum register is BASS (pitch range: 41 to 64).
- **CONTROL_MIN_REGISTER__baritone:** Minimum register is BARITONE (pitch range: 45 to 65).
- **CONTROL_MIN_REGISTER__tenor:** Minimum register is TENOR (pitch range: 48 to 69).
- **CONTROL_MIN_REGISTER__alto:** Minimum register is ALTO (pitch range: 55 to 76).
- **CONTROL_MIN_REGISTER__contralto:** Minimum register is CONTRALTO (pitch range: 53 to 74).
- **CONTROL_MIN_REGISTER__mezzo_soprano:** Minimum register is MEZZO_SOPRANO (pitch range: 57 to 78).
- **CONTROL_MIN_REGISTER__soprano:** Minimum register is SOPRANO (pitch range: 60 to 81).
- **CONTROL_MIN_REGISTER__sopranissimo:** Minimum register is SOPRANISSIMO (pitch range: 74 to 95).
- **CONTROL_MIN_REGISTER__highest:** Minimum register is HIGHEST (pitch range: 81 to 130).
- **CONTROL_SPECIAL_NOTE__h1:** Special note is the second note of the chromatic scale (h1).
- **CONTROL_SPECIAL_NOTE__h10:** Special note is the eleventh note of the chromatic scale (h10).
- **CONTROL_SPECIAL_NOTE__h11:** Special note is the twelfth note of the chromatic scale (h11).
- **CONTROL_SPECIAL_NOTE__h2:** Special note is the third note of the chromatic scale (h2).
- **CONTROL_SPECIAL_NOTE__h3:** Special note is the fourth note of the chromatic scale (h3).
- **CONTROL_SPECIAL_NOTE__h4:** Special note is the fifth note of the chromatic scale (h4).
- **CONTROL_SPECIAL_NOTE__h6:** Special note is the seventh note of the chromatic scale (h6).
- **CONTROL_SPECIAL_NOTE__h8:** Special note is the ninth note of the chromatic scale (h8).
- **CONTROL_SPECIAL_NOTE__h9:** Special note is the tenth note of the chromatic scale (h9).
- **CONTROL_SPECIAL_NOTE__s1:** Special note is the second note of the diatonic scale (s1).
- **CONTROL_SPECIAL_NOTE__s3:** Special note is the fourth note of the diatonic scale (s3).
- **CONTROL_SPECIAL_NOTE__s5:** Special note is the sixth note of the diatonic scale (s5).





Example
---------


In the following example we constraint the model to generate a piano track with a dense monophonic melody and
constraint the second bar of the bass track to use a quite high register ::


    import os
    from maidi import MidiScore, instrument
    import maidi.chords_symbols as cs
    from maidi.integrations.api import MusicLangAPI

    # Assuming API_KEY is set in the environment
    API_KEY = os.getenv("API_KEY")

    # Create a 4 bar template with the given instruments
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO, instrument.ACOUSTIC_BASS], nb_bars=5, ts=(4, 4), tempo=120
    )
    # Get the controls (the prompt) for this score
    mask, tags, chords = score.get_empty_controls(prevent_silence=True)
    mask[:, :] = 1  # Regenerate everything in the score

    # Let control the tags
    for i in range(mask.shape[1]):
        tags[0][i] = ['CONTROL_DENSITY__HIGH', 'CONTROL_MAX_POLYPHONY__1']

    # Second bar of the bass track use a quite high register (like alto)
    tags[1][1] = ['CONTROL_MIN_REGISTER__alto', 'CONTROL_MAX_REGISTER__alto']

    # Call the musiclang API to predict the score
    api = MusicLangAPI(api_key=API_KEY, verbose=True)
    predicted_score = api.predict(score,
                                  mask, tags=tags, chords=chords, async_mode=False, polling_interval=3
                                  )
    predicted_score.write("predicted_score.mid")




Automatically tag a score
--------------------------

M(AI)DI provides a feature to automatically extract the tags from a score. So you can do analysis of a given score
or even use it as a prompt for the model to generate a music that "looks alike" the analyzed one.

The following example shows how to extract the tags from a given score ::


    from maidi.analysis import tags_providers

    score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))

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
    print(tags)
    print(chords)




