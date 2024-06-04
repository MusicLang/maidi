from maidi import MidiScore

# Assuming API_URL and API_KEY are set in the environment

filepath = "examples/example1.mid"

score = MidiScore.from_midi(
    filepath, chord_range=(0, 8)
)  # Load first 8 bars of the midi file
mask, tags, chords = (
    score.get_empty_controls()
)  # Get the controls (the raw prompt) for this score
mask[:, :] = 1  # Regenerate everything in the score with the same instruments

predicted_score = score.predict(mask, async_mode=False)
predicted_score.write("predicted_score.mid")
