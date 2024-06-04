
from midi_parser import MusicLangScore


# Assuming API_URL and API_KEY are set in the environment

filepath = "examples/example1.mid"

score = MusicLangScore.from_midi(filepath, chord_range=(0, 8)) # Load first 8 bars of a midi file
mask = score.get_mask()
mask[:, :] = 1  # Regenerate everything in the score with the same instruments

task_id = score.predict(mask, async_mode=True)
