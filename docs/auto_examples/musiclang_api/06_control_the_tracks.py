"""
Deep musical control over the generation
===================================================

MusicLang allows you to control the chord progression of your song. In this example :

- We constrain the model to generate a piano track with a dense monophonic melody
- We constrain the second bar of the bass track to use a quite high register

By using and modifying this example you will be able to add deep control over the music generated with musiclang

Check :ref:`tags` to get the full list of available tags

"""

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