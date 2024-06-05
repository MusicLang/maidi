import os

from maidi import MidiScore, ScoreTagger
from maidi.analysis import tags_providers
from maidi.integrations.api import MusicLangAPI

filepath = "examples/example1.mid"

score = MidiScore.from_midi(
    filepath, chord_range=(0, 16)
)  # Load first 8 bars of a midi file

tagger = ScoreTagger(
    [
        tags_providers.DensityTagsProvider(),
        tags_providers.MinMaxPolyphonyTagsProvider(),
        tags_providers.MinMaxRegisterTagsProvider(),
        tags_providers.SpecialNotesTagsProvider(),
    ]
)

tags = tagger.tag_score(score)
chords = score.get_chords_prompt()
# Generate a song from scratch with these tags
mask, _, _ = score.get_empty_controls(prevent_silence=True)
mask[:, :] = 1  # Regenerate everything in the score

# Call the musiclang API to predict the score
# Assuming API_URL and API_KEY are set in the environment
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

api = MusicLangAPI(API_URL, API_KEY, verbose=True)
predicted_score = api.predict(score,
    mask, tags=tags, chords=chords, async_mode=False, polling_interval=5,
                              temperature=0.9
)
predicted_score.write("predicted_score.mid")