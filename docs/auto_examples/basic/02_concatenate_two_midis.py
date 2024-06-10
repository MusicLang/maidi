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

print('Score1 shape: ', score1.shape)
print('Score2.shape', score2.shape)

horizontally_concatenated_score = score1.concatenate(score2, axis=1)
horizontally_concatenated_score.write("horizontally_concatenated_score.mid")

print('New horizontally concatenated score shape :', horizontally_concatenated_score.shape)
# We could also concatenate the scores vertically (add new tracks keeping the same duration)
vertically_concatenated_score = score1.concatenate(score2, axis=0)

print('New vertically concatenated score shape :', vertically_concatenated_score.shape)
