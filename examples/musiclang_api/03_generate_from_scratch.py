"""
Create a drum'n'bass sample
==================================================

In this example :
- We directly generate a drum'n'bass sample from scratch using the `generate_from_scratch` method of the MusicLang API
- We save the predicted score to a midi file

"""

from maidi import MidiScore
from maidi import instrument
from maidi.integrations.api import MusicLangAPI
import os

# Assuming API_URL and MUSICLANG_API_KEY are set in the environment
# Call the musiclang API to predict the score
api = MusicLangAPI(api_key=os.getenv("MUSICLANG_API_KEY"), verbose=True)

instruments = [instrument.DRUMS, instrument.ELECTRIC_BASS_FINGER]
nb_bars = 4
time_signature = (4, 4)
tempo = 120

predicted_score = api.generate_from_scratch(instruments=instruments, nb_bars=nb_bars, ts=time_signature, tempo=tempo)
predicted_score.write("predicted_score.mid")