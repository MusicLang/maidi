"""
Concatenate two midis
==================================================

In this example :
- We will concatenate two midi files horizontally
- Then vertically
"""

from maidi import MidiScore, midi_library


score1 = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
score2 = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))

horizontally_concatenated_score = score1.concatenate(score2, axis=1)
horizontally_concatenated_score.write("horizontally_concatenated_score.mid")


# We could also concatenate the scores vertically (add new tracks keeping the same duration)
vertically_concatenated_score = score1.concatenate(score2, axis=0)
