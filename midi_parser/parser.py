import symusic
import numpy as np
from fractions import Fraction as frac
from symusic import Track, TimeSignature, Note, Score, Tempo
import time

from .chord_inference import fast_chord_inference

class Parser:
    """
    Parser class to extract and write midi files
    """

    def __init__(self, debug=False, separate_voices=False, tpq=24, min_dur=1):
        self.tpq = tpq
        self.min_dur = min_dur
        self.debug = debug
        self.separate_voices = separate_voices

    def get_bars(self, score):
        # Calculate bars
        time_signatures = score.time_signatures
        time_signatures = sorted(time_signatures, key=lambda x: x.time)
        if len(time_signatures) == 0:
            time_signatures = [TimeSignature(0, 4, 4)]
        ticks_per_quarter = score.ticks_per_quarter
        chord_durations = []
        time = 0
        bars = []
        while time < score.end():
            start_time = time
            end_time, num, den = self.get_end_of_bar(time, time_signatures, ticks_per_quarter)
            chord_durations.append((num, den))
            bars.append((start_time, end_time))
            time = end_time
        return bars, chord_durations

    def get_bar_nb_array_optimized(self, note_times, bars):
        # Convert bars to a NumPy array for efficient computation
        bars_array = np.array(bars)
        start_times = bars_array[:, 0]
        end_times = bars_array[:, 1]

        # Use broadcasting to find which bar each note belongs to
        # Note times are broadcast across the start and end times of bars to create a 2D boolean array
        in_bar = (note_times['time'][:, None] >= start_times) & (note_times['time'][:, None] < end_times)

        # Get the bar indices for each note. The result is a 2D array where each row has a single True value
        bar_indices = np.argmax(in_bar, axis=1)

        # Handle notes that do not fall within any bar by setting their bar index to a special value (e.g., -1)
        # This step is optional and depends on how you want to handle such cases
        outside_bars = ~in_bar.any(axis=1)
        bar_indices[outside_bars] = -1

        return bar_indices

    def get_end_of_bar(self, bar_start, time_signatures, ticks_per_quarter):
        # Find time signature
        # We use a tolrance of one quarter note to find the time signature
        res = [ts for ts in time_signatures if bar_start >= (ts.time - ticks_per_quarter//2)]
        time_signature = res[-1] if len(res) > 0 else TimeSignature(0, 4, 4)

        num = time_signature.numerator
        den = time_signature.denominator
        duration = 4 * frac(num, den)
        return int(bar_start + duration * ticks_per_quarter), num, den

    def groupby_bar(self, score_soa, bars):
        # Group SOA by bar
        bar_nb_array = score_soa['bar']
        # Time is relative to the start of the bar in our notation
        del score_soa['bar']
        result = [{k: score_soa[k][bar_nb_array == bar_nb] for k in score_soa.keys()} for bar_nb in range(len(bars))]
        return result


    def groupby_voices(self, tracks, program_voices_offset):
        new_tracks = {}
        for track_key, bars in tracks.items():
            # Determine the number of bars to ensure every voice has an entry for each bar
            num_bars = len(bars)

            # Initialize track_voices with an entry for each voice for each bar, even if empty
            track_voices = {}
            for bar_idx, bar in enumerate(bars):
                if 'voices' in bar:
                    unique_voices = np.unique(bar['voices'])
                else:
                    unique_voices = [0]  # Default voice if not specified

                for voice in unique_voices:
                    voice_key = (*track_key, voice)
                    if voice_key not in track_voices:
                        # Initialize with empty lists for each bar to ensure perfect mapping
                        track_voices[voice_key] = [{} for _ in range(num_bars)]

                    if 'voices' in bar:
                        # Select notes belonging to the current voice
                        mask = bar['voices'] == voice
                        bar_for_voice = {k: v[mask] for k, v in bar.items() if k != 'voices'}
                    else:
                        # If no voice separation, use the bar as is
                        bar_for_voice = bar

                    # Update the specific bar for the voice
                    track_voices[voice_key][bar_idx] = bar_for_voice

            # Update new_tracks with segregated bars
            new_tracks.update(track_voices)

        # Replace original tracks with newly segregated ones
        tracks.clear()
        tracks.update(new_tracks)


    def pprint(self, *text):
        if self.debug:
            print(*text)

    def get_notes(self, bars, score):
        tracks = [t.notes for t in score.tracks if len(t.notes) > 0]
        data = {"bars": [], "tracks": []}
        for track in tracks:
            track_notes = []
            for idx, bar in enumerate(bars):
                start_bar, end_bar = bar
                data['bars'].append({"start": start_bar, "end": end_bar})
                # Transform to time, duration, pitch, velocity
                bar_notes = [[n.time - start_bar, n.duration, n.pitch, n.velocity] for n in track if start_bar <= n.time < end_bar]
                track_notes.append(bar_notes)
            data['tracks'].append(track_notes)

        return data


    @staticmethod
    def add_default_track_events(track):
        from symusic import ControlChange
        #track.controls = [ControlChange(0, 0, 0)]
        track.notes = [Note(0, 2, 60, 1)]

    def add_track(self, midi_file, output_midi_file, instrument):
        """
        Add a track to the midi file and save it
        :param midi_file:
        :param program:
        :param is_drum:
        :return:
        """
        program, is_drum = instrument
        score_quantized = self.preload_score(midi_file)
        track = Track(program=program, is_drum=bool(is_drum))
        self.add_default_track_events(track)
        score_quantized.tracks.append(track)
        score_quantized.dump_midi(output_midi_file)

    def remove_track(self, midi_file, output_midi_file, index):
        score_quantized = self.preload_score(midi_file)
        score_quantized.tracks.pop(index)
        score_quantized.dump_midi(output_midi_file)

    def change_program(self, file, output_file, track, param):

        program, is_drum = param
        score = symusic.Score(file, ttype="tick")
        score_quantized = score.resample(tpq=self.tpq, min_dur=self.min_dur)
        score_quantized.tracks[track].program = program
        score_quantized.tracks[track].is_drum = bool(is_drum)
        score_quantized.dump_midi(output_file)

    def preload_score(self, midi_file):
        from symusic import Track
        score = symusic.Score(midi_file, ttype="tick")
        score_quantized = score.resample(tpq=self.tpq, min_dur=self.min_dur)
        return score_quantized

    def add_tracks(self, midi_file, output_midi_file, programs):
        score_quantized = self.preload_score(midi_file)
        for program, is_drum in programs:
            track = Track(program=program, is_drum=is_drum == 1)
            self.add_default_track_events(track)
            score_quantized.tracks.append(track)
        score_quantized.dump_midi(output_midi_file)
    def get_base_masking_grid(self, midi_file, chord_range=None):
        score = symusic.Score(midi_file, ttype="tick")
        score_quantized = score.resample(tpq=self.tpq, min_dur=self.min_dur)
        bars, chord_durations = self.get_bars(score_quantized)

        # Create a masking grid with 0 of size num_tracks x num_bars
        masking_grid = np.zeros((len(score_quantized.tracks), len(bars)), dtype=np.int8)
        return masking_grid

    def get_mask_and_tracks(self, midi_file, chord_range=None):
        from .constants import REVERSE_INSTRUMENT_DICT
        score = symusic.Score(midi_file, ttype="tick")
        score_quantized = score.resample(tpq=self.tpq, min_dur=self.min_dur)
        bars, chord_durations = self.get_bars(score_quantized)

        if chord_range is None:
            chord_range = (0, len(bars))
        last_chord_index = min(chord_range[1], len(bars)) - 1
        end_time = bars[last_chord_index][1]
        start_time = bars[chord_range[0]][0]
        # Create a masking grid with 0 of size num_tracks x num_bars
        masking_grid = np.zeros((len(score_quantized.tracks), len(bars)), dtype=np.int8)
        tracks = []
        for idx, track in enumerate(score_quantized.tracks):
            is_drum = track.is_drum
            program = track.program if not is_drum else 0
            instrument = REVERSE_INSTRUMENT_DICT.get((program, is_drum), "piano")
            track.notes = [n for n in track.notes if start_time <= n.time < end_time]
            # If track empty add notes
            tracks.append(instrument)
            if len(track.notes) == 0:
                # Add a fake control change to prevent empty track from being removed
                self.add_default_track_events(track)

        bars = bars[chord_range[0]:chord_range[1]]
        notes = self.get_notes(bars, score_quantized)
        return masking_grid, tracks, score_quantized, notes

    def write(self, chords, tracks, track_keys, tempo):
        score = Score(ttype=self.tpq)
        score.tempos.append(Tempo(0, tempo))
        current_ts = None
        for chord in chords:
            ts = TimeSignature(chord[7], chord[5], chord[6])
            candidate_ts = (ts.numerator, ts.denominator)
            if current_ts != candidate_ts:
                score.time_signatures.append(ts)
                current_ts = (ts.numerator, ts.denominator) if current_ts is None else current_ts

        for track_key in track_keys:
            idx, program, is_drum, voice = track_key
            track = Track(program=program, is_drum=is_drum)
            track.notes = tracks[(idx, program, is_drum, voice)]
            score.tracks.append(track)
        return score

    def extract_midi(self, output_midi_file, midi_file, chord_range=None):
        chords, tracks, track_keys, tempo = self.parse(midi_file, chord_range)
        score = self.write(chords, tracks, track_keys, tempo)
        score.dump_midi(output_midi_file)

    def parse(self, midi_file, chord_range=None, from_end=False):
        start = time.time()
        score_quantized = self.preload_score(midi_file)
        tempo = score_quantized.tempos[0].qpm if len(score_quantized.tempos) > 0 else 120

        self.pprint("Resampling time: ", time.time() - start)
        start = time.time()
        bars, chord_durations = self.get_bars(score_quantized)
        self.pprint("Getting bars time: ", time.time() - start)
        tracks = {}
        track_keys = []
        tracks_global = {}
        start = time.time()

        if chord_range is None:
            chord_range = (0, len(bars))

        program_voices_offset = {}

        for idx, track in enumerate(score_quantized.tracks):
            is_drum = track.is_drum
            program = track.program if not is_drum else 0
            score_soa = track.notes.numpy()  # Convert to a dict of arrays
            track_keys.append((idx, program, is_drum, 0))
            # Get track between chord range
            if chord_range is not None:
                start_time = bars[chord_range[0]][0]
                last_chord_index = min(chord_range[1], len(bars)) - 1
                end_time = bars[last_chord_index][1]
                mask = (score_soa['time'] >= start_time) & (score_soa['time'] < end_time)
                for k, v in score_soa.items():
                    score_soa[k] = v[mask]

            score_soa['bar'] = self.get_bar_nb_array_optimized(score_soa, bars)
            score_soa['start_bar_tick'] = np.array([bars[bar_nb][0] for bar_nb in score_soa['bar']])
            score_soa['time'] -= score_soa['start_bar_tick']
            del score_soa['start_bar_tick']
            # Group SOA by bar
            grouped_score = self.groupby_bar(score_soa, bars)
            # If chord range is specified, keep only the specified chords
            if chord_range is not None:
                grouped_score = grouped_score[chord_range[0]:chord_range[1]]

            tracks[(idx, program, is_drum)] = grouped_score

        self.pprint("Grouping time: ", time.time() - start)
        start = time.time()
        # Now we have a dict of arrays for each track, grouped by bar, let's do the voice separation
        start = time.time()
        chords = fast_chord_inference(tracks, chord_durations)
        chords = [list(c) + list(b) for c, b in zip(chords, bars)] # Add bar start, bar end
        self.pprint("Chord inference time: ", time.time() - start)
        start = time.time()
        self.groupby_voices(tracks, program_voices_offset)
        self.pprint("Voice groupby time: ", time.time() - start)
        return chords, tracks, track_keys, tempo


