from maidi import MidiScore

# Assuming API_URL and API_KEY are set in the environment

instruments = ["drums_0", "electric_bass_finger", "clean_guitar", "overdriven_guitar"]
nb_bars = 8
time_signature = (4, 4)
tempo = 90

# Create a 8 bar template
score = MidiScore.from_empty(
    instruments=instruments, nb_bars=nb_bars, ts=time_signature, tempo=tempo
)

# Get the controls (the prompt) for this score
mask, tags, chords = score.get_empty_controls(prevent_silence=True)
mask[:, :] = 1  # Regenerate everything in the score with the same instruments


predicted_score = score.predict(
    mask, tags=tags, chords=chords, async_mode=False, polling_interval=5
)
predicted_score.write("predicted_score.mid")
