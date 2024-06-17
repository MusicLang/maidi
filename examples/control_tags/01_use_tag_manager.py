from maidi import MidiScore, TagManager, instrument, Tags
from maidi.integrations.api import MusicLangAPI

api = MusicLangAPI(verbose=True)


score = MidiScore.from_empty(
    instruments=[instrument.DRUMS, instrument.PAD_HALO, instrument.ALTO_SAX, instrument.ELECTRIC_BASS_FINGER],
    nb_bars=8,
    ts=(4, 4),
    tempo=100
)
mask = score.get_mask()
tags = TagManager.empty_from_score(score)

# Assign tags and mask
tags[0, :1] = Tags.density.high  # drums
tags[1, 0:1] = [Tags.density.medium, Tags.min_polyphony.four, Tags.max_polyphony.four] # pad
tags[2, 0:1] = [Tags.min_polyphony.one, Tags.max_polyphony.one, Tags.special_notes.ninth, Tags.min_register.alto, Tags.max_register.contralto]
tags[3, 0:1] = [Tags.min_polyphony.one, Tags.max_polyphony.one]
mask[:, :] = 1

predicted_score = api.predict(score, mask=mask, tags=tags.tags, temperature=0.9)
predicted_score.write('predicted_score.mid')


