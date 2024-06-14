"""
Generate a new track on a midi file
======================================================

In this example :
- We load a 4 bar template from a midi file
- We add a clean guitar track
- We call the musiclang API to predict the score
- We save the predicted score to a midi file

"""


import os
from maidi import MidiScore, instrument, midi_library
from maidi.integrations.api import MusicLangAPI

# Assuming API_URL and MUSICLANG_API_KEY are set in the environment
MUSICLANG_API_KEY = os.getenv("MUSICLANG_API_KEY")

# Create a 4 bar template with the given instruments
score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
# Add a clean guitar track and set the mask
score = score.add_instrument(instrument.CLEAN_GUITAR)
mask, _, _ = score.get_empty_controls(prevent_silence=True)
mask[-1, :] = 1  # Generate the last track

# Call the musiclang API to predict the score
api = MusicLangAPI(MUSICLANG_API_KEY, verbose=True)
predicted_score = api.predict(score,
    mask, async_mode=False, polling_interval=3
)
predicted_score.write("predicted_score.mid")