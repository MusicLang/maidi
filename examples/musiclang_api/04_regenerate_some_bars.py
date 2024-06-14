"""
Regenerate only some bars of a specific tracks
======================================================

In this example :
- We load a 4 bar template from a midi file (drum and bass
- We regenerate only the first and last bar of the bass (second track)

"""


import os
from maidi import MidiScore, instrument, midi_library
from maidi.integrations.api import MusicLangAPI

# Assuming API_URL and MUSICLANG_API_KEY are set in the environment
API_URL = os.getenv("API_URL")
MUSICLANG_API_KEY = os.getenv("MUSICLANG_API_KEY")

# Create a 4 bar template with the given instruments
score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
mask, _, _ = score.get_empty_controls(prevent_silence=True)

# Let's set the mask to regenerate the bar we want
mask[1, 0] = 1  # Second track, first bar
mask[1, -1] = 1  # Second track last bar

# Call the musiclang API to predict the score
api = MusicLangAPI(api_key=MUSICLANG_API_KEY, verbose=True)
predicted_score = api.predict(score,
    mask, async_mode=False, polling_interval=3
)
predicted_score.write("predicted_score.mid")