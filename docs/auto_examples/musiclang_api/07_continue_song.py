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
from maidi import chords_symbols as cs

# Assuming API_URL and API_KEY are set in the environment
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

nb_bars_extension = 4

# Load a score with two tracks and 4 bars (drum and bass)
score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))

# Control the chord progression, same as before (Optional)
chords = [
            (cs.I, cs.C, cs.major, cs._root_position),
           (cs.VI, cs.C, cs.major, ''), # Triad in root position can also be written as empty string ''
           (cs.II, cs.C, cs.major, cs._6),
           (cs.V, cs.C, cs.major, cs._7),
]

# Add some tags for the new bars (Optional)
tags = [[['CONTROL_MIN_POLYPHONY__1', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_DENSITY__LOW'] for bar_index in range(nb_bars_extension)]
        for track_index in range(score.nb_tracks)
        ]

# Call the musiclang API to predict the score
api = MusicLangAPI(api_key=API_KEY, verbose=True)
predicted_score = api.extend(score,
                             nb_bars_extension,  #  How many bars to add to the current score
                             chords=chords,
                             tags=tags,
                             nb_added_bars_step=2,  # Choose how many bar generate per steps (if none it is calculated automatically)
                             async_mode=False, polling_interval=3
)
predicted_score.write("predicted_score.mid")