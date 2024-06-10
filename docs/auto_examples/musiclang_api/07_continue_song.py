"""
Extend an existing sample or song
======================================================

In this example :
- We load an existing song
- We ask musiclang to continue it for 4 bars

"""


import os
from maidi import MidiScore, instrument, midi_library
from maidi.integrations.api import MusicLangAPI

# Assuming API_URL and API_KEY are set in the environment
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

nb_bars_extension = 4

# Create a 4 bar template with the given instruments
score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))

# Call the musiclang API to predict the score
api = MusicLangAPI(api_key=API_KEY, verbose=True)
predicted_score = api.extend(score, nb_bars_extension, async_mode=False, polling_interval=3
)
predicted_score.write("predicted_score.mid")