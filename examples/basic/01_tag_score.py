"""
Tag each bar of a score with musical informations
==================================================

In this example :
- We load an existing score from the example library
- We tag each bar of the score with musical informations
- We print the tags
"""

from maidi import MidiScore, ScoreTagger, midi_library
from maidi.analysis import tags_providers

score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))
tagger = ScoreTagger(
    [
        tags_providers.DensityTagsProvider(),
        tags_providers.MinMaxPolyphonyTagsProvider(),
        tags_providers.MinMaxRegisterTagsProvider(),
        tags_providers.SpecialNotesTagsProvider(),
    ]
)

tags = tagger.tag_score(score)
chords = score.get_chords()
print(tags)
print(chords)