"""
Control the chord progression of the generation
===================================================

MusicLang allows you to control the chord progression of your song. In this example :

- We generate a 5 bars song with a classic I vi ii6 V7 chord progression
- We let the model decide the last bar chord

By using and modifying this example you can create a features that involves enforcing a given chord progression.

Check :ref:`chords` to check the chord scale progression syntax.

"""

import os
from maidi import MidiScore, instrument
import maidi.chords_symbols as cs
from maidi.integrations.api import MusicLangAPI

# Assuming API_URL and API_KEY are set in the environment
API_KEY = os.getenv("API_KEY")

# Create a 4 bar template with the given instruments
score = MidiScore.from_empty(
    instruments=[instrument.ELECTRIC_PIANO], nb_bars=5, ts=(4, 4), tempo=120
)
# Get the controls (the prompt) for this score
mask, tags, chords = score.get_empty_controls(prevent_silence=True)
mask[:, :] = 1  # Regenerate everything in the score

# We control the chord progression here (I, vi, ii6, V7, unspecified in D major) :

chords = [(cs.I, cs.D, cs.major, cs._root_position),
           (cs.VI, cs.D, cs.major, ''), # Triad in root position can also be written as empty string ''
           (cs.II, cs.D, cs.major, cs._6),
           (cs.V, cs.D, cs.major, cs._7),
           None  # Let the model choose the last chord
          ]

# Call the musiclang API to predict the score
api = MusicLangAPI(api_key=API_KEY, verbose=True)
predicted_score = api.predict(score,
    mask, tags=tags, chords=chords, async_mode=False, polling_interval=3
)
predicted_score.write("predicted_score.mid")

