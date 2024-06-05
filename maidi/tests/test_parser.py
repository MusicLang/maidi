import pytest
import tempfile
import os
from maidi import Parser

def create_fake_midi_file(filename):
    import pretty_midi
    import numpy as np
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


def test_parser():

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=True) as f:
        create_fake_midi_file(f.name)
        parser = Parser()
        chords, tracks, track_keys, tempo = parser.parse(midi_file=f.name)
        assert len(track_keys) == 2
        assert len(chords) == 2





