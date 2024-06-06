"""
Create a 4 bars drum'n'bass song with MusicLangAPI
==================================================

In this example :
- We create an empty score with 4 bars and drums and bass instruments
- We set the mask to regenerate everything
- We call the musiclang API to generate the score
- We save the predicted score to a midi file

"""

from maidi import MidiScore
from maidi import instrument
from maidi.integrations.api import MusicLangAPI
import os

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
    mask, tags=tags, chords=chords, async_mode=False, polling_interval=3
)
predicted_score.write("predicted_score.mid")