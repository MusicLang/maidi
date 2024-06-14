"""
Create a transition between two parts of a song
======================================================

In this example :
- We load two parts of a same song (midi file with same tracks)
- We ask musiclang to create a 4-bar transition for us between those two tracks
- We get back the score with only the transition OR the full score

"""


import os
from maidi import MidiScore, instrument, midi_library
from maidi.integrations.api import MusicLangAPI

# Assuming API_URL and MUSICLANG_API_KEY are set in the environment
API_URL = os.getenv("API_URL")
MUSICLANG_API_KEY = os.getenv("MUSICLANG_API_KEY")

nb_bars_transition = 4  # Should be less than 12 bars, the higher the value the less context is added to the model

# Create a 4 bar template with the given instruments
score1 = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
score2 = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))

# Call the musiclang API to predict the score
api = MusicLangAPI(api_key=MUSICLANG_API_KEY, verbose=True)
predicted_score = api.create_transition(score1, score2, nb_bars_transition,
                                        async_mode=False, polling_interval=3
)
predicted_score.write("predicted_score.mid")