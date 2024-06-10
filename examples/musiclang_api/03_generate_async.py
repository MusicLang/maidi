"""
Create a song in async mode
======================================================

In this example :
- We do the same example that 02_generate_from_scratch.py but in async mode
- We poll the API until the prediction is done every 3 seconds

"""

import os
import time
from maidi import MidiScore
from maidi import instrument
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
api = MusicLangAPI(api_key=API_KEY, verbose=True)
task_id = api.predict(score,
                              mask,
                              tags=tags,
                              chords=chords,
                              async_mode=True, # Set to True to use async mode

                              polling_interval=3
)

# Poll the API until the prediction is done
while True:
    score = api.poll_api(task_id)
    if score is not None:
        score.write('predicted_score.mid')
        break
    time.sleep(3)
