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
    instrument.CLEAN_GUITAR,
    instrument.OVERDRIVEN_GUITAR
]

nb_bars = 8
time_signature = (4, 4)
tempo = 90


# Create a 8 bar template with the given instruments
score = MidiScore.from_empty(
    instruments=instruments, nb_bars=nb_bars, ts=time_signature, tempo=tempo
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
