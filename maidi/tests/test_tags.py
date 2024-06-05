from maidi.analysis import ScoreTagger
from maidi.analysis import tags_providers
from maidi import MidiScore

import tempfile

def create_fake_midi_file(filename):
    import pretty_midi
    # Create a PrettyMIDI object
    midi_data = pretty_midi.PrettyMIDI()
    # Create an Instrument instance
    instrument1 = pretty_midi.Instrument(program=0)
    instrument2 = pretty_midi.Instrument(program=10)
    instruments = [instrument1, instrument2]

    pitches = [60, 64, 67]
    times = [(0, 1), (1, 2), (2, 3), (3, 4)]
    for instrument in instruments:
        # Iterate over note names, which will be converted to note number later
        for start, end in times:
            for pitch in pitches:
                # Create a Note instance, starting at 0s and ending at 1s
                note = pretty_midi.Note(
                    velocity=100, pitch=pitch, start=start, end=end)
                # Add it to our instrument
                instrument.notes.append(note)
        # Add the instrument to the PrettyMIDI object
        midi_data.instruments.append(instrument)
        # Write out the MIDI data
    midi_data.write(filename)


def test_basic_density_tags_with_score_tagger():
    with tempfile.NamedTemporaryFile(suffix='.mid', delete=True) as f:
        create_fake_midi_file(f.name)
        score_tagger = ScoreTagger([
            tags_providers.DensityTagsProvider()
        ])

        score = MidiScore.from_midi(f.name)
        tags = score_tagger.tag_score(score)

        assert len(tags) == 2
        assert len(tags[0]) == 2
        assert len(tags[0][0]) == 1




