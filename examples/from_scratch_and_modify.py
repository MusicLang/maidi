from midi_parser import MusicLangScore
from midi_parser.constants import INSTRUMENTS_DICT

#Assuming API_URL and API_KEY are set in the environment
score = MusicLangScore.from_empty(instruments=['drums_0', 'electric_bass_finger', 'clean_guitar', 'overdriven_guitar'], nb_bars=8, ts=(4, 4), tempo=90) # Load first 8 bars of a midi file
mask, tags, chords = score.get_empty_controls(prevent_silence=True)
chords[0] = [0, 0, 'm', '']
chords[1] = [3, 3, 'M', '']

LAST_INDEX = 3
tags[LAST_INDEX][0] = ['CONTROL_DENSITY__LOWER', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_MIN_REGISTER__soprano', 'CONTROL_MAX_REGISTER__soprano']
tags[LAST_INDEX][1] = ['CONTROL_DENSITY__LOWER', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_MIN_REGISTER__soprano', 'CONTROL_MAX_REGISTER__soprano']
tags[LAST_INDEX][2] = ['CONTROL_DENSITY__LOWER', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_MIN_REGISTER__soprano', 'CONTROL_MAX_REGISTER__soprano']
tags[LAST_INDEX][3] = ['CONTROL_DENSITY__LOWER', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_MIN_REGISTER__soprano', 'CONTROL_MAX_REGISTER__soprano']

mask[:, :] = 1  # Regenerate everything in the score with the same instruments


predicted_score = score.predict(mask, tags=tags, chords=chords, async_mode=False, polling_interval=5)
predicted_score.write('data/predicted_score.mid')


base_score = MusicLangScore.from_midi('data/predicted_score.mid')
mask, tags, chords = base_score.get_empty_controls(prevent_silence=False)
mask[:, :] = 1  # Regenerate everything in the score with the same instruments

# Replace two first bars
mask[:, :] = 0
mask[LAST_INDEX, :4] = 1
chords[0] = [0, 0, 'm', '']
chords[1] = [4, 3, 'M', '']

# Add tags to use ninths chords and high density
tags[LAST_INDEX][0] = ['CONTROL_DENSITY__MEDIUM', 'CONTROL_SPECIAL_NOTE__s1', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_MIN_REGISTER__soprano', 'CONTROL_MAX_REGISTER__soprano']
tags[LAST_INDEX][1] = ['CONTROL_DENSITY__MEDIUM', 'CONTROL_SPECIAL_NOTE__s1', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_MIN_REGISTER__soprano', 'CONTROL_MAX_REGISTER__soprano']
tags[LAST_INDEX][2] = ['CONTROL_DENSITY__MEDIUM', 'CONTROL_SPECIAL_NOTE__s1', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_MIN_REGISTER__soprano', 'CONTROL_MAX_REGISTER__soprano']
tags[LAST_INDEX][3] = ['CONTROL_DENSITY__MEDIUM', 'CONTROL_SPECIAL_NOTE__s1', 'CONTROL_MAX_POLYPHONY__1', 'CONTROL_MIN_REGISTER__soprano', 'CONTROL_MAX_REGISTER__soprano']


predicted_score = base_score.predict(mask, tags=tags, chords=chords, async_mode=False)
predicted_score.write('data/predicted_score_with_tags.mid')


