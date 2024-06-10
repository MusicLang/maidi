import symusic
import numpy as np
from fractions import Fraction as frac
from symusic import Track, TimeSignature, Note, Score, Tempo
import time

from maidi.chords.chord_inference import fast_chord_inference


class Parser:
    """
    Low level parser class to read and write midi files
    You probably don't need to use this class directly, use MidiScore instead

    Usage:
    ------
    ```python

    from maidi.parser import Parser
    parser = Parser()
    chords, tracks, track_keys, tempo = parser.parse("input.mid")
    score = parser.write(chords, tracks, track_keys, tempo)
    score.dump_midi("output.mid")

    ```
    """

    def __init__(self, verbose=False, tpq=24, min_dur=1):
        """
        Initialize the parser
        Parameters
        ----------
        verbose : bool
            Whether to print debug information
        tpq : int (Default value = 24)
            Ticks per quarter note for the midi file, it will be resampled to this value
        min_dur : int (Default value = 1)
            Minimum duration for a note in ticks
        """
        self.tpq = tpq
        self.min_dur = min_dur
        self.verbose = verbose

    def parse(self, midi_file, chord_range=None):
        """

        Parameters
        ----------
        midi_file : str
            Path to the midi file to parse

        chord_range : tuple or None (Default value = None)
            Tuple with the start and end chord index to parse. If None, parse the whole file

        Returns
        -------
        chords : list
            List of chords with the time signature of each bar
        tracks : dict
            Dict of arrays with the notes for each track
        track_keys : list
            List of tuples with the track keys (program, is_drum, voice)

        """
        start = time.time()
        score_quantized = self._preload_score(midi_file)
        tempo = (
            score_quantized.tempos[0].qpm if len(score_quantized.tempos) > 0 else 120
        )

        self.pprint("Resampling time: ", time.time() - start)
        start = time.time()
        bars, chord_durations = self._get_bars(score_quantized)
        self.pprint("Getting bars time: ", time.time() - start)
        tracks = {}
        track_keys = []
        tracks_global = {}
        start = time.time()

        if chord_range is None:
            chord_range = (0, len(bars))


        for idx, track in enumerate(score_quantized.tracks):
            is_drum = track.is_drum
            program = track.program if not is_drum else 0
            score_soa = track.notes.numpy()  # Convert to a dict of arrays
            track_keys.append((idx, program, is_drum))
            # Get track between chord range
            if chord_range is not None:
                start_time = bars[chord_range[0]][0]
                last_chord_index = min(chord_range[1], len(bars)) - 1
                end_time = bars[last_chord_index][1]
                mask = (score_soa["time"] >= start_time) & (
                        score_soa["time"] < end_time
                )
                for k, v in score_soa.items():
                    score_soa[k] = v[mask]

            score_soa["bar"] = self._get_bar_nb_array_optimized(score_soa, bars)
            score_soa["start_bar_tick"] = np.array(
                [bars[bar_nb][0] for bar_nb in score_soa["bar"]]
            )
            score_soa["time"] -= score_soa["start_bar_tick"]  # Make time relative to the start of the bar
            del score_soa["start_bar_tick"]
            # Group SOA by bar
            grouped_score = self._groupby_bar(score_soa, bars)
            # If chord range is specified, keep only the specified chords
            if chord_range is not None:
                grouped_score = grouped_score[chord_range[0]: chord_range[1]]

            tracks[(idx, program, is_drum)] = grouped_score

        self.pprint("Grouping time: ", time.time() - start)
        # Now we have a dict of arrays for each track, grouped by bar, let's do the chord inference
        start = time.time()
        chords = fast_chord_inference(tracks, chord_durations)
        self.pprint("Chord inference time: ", time.time() - start)
        return chords, tracks, track_keys, tempo

    def write(self, chords, tracks, track_keys, tempo):
        """
        Write a score from the parsed data.
        You probably don't need to use this method directly, use MidiScore.write instead

        Parameters
        ----------
        chords : list
            List of chords with the time signature of each bar

        tracks : dict
            Dict of arrays with the notes for each track

        track_keys : list
            List of tuples with the track keys (program, is_drum, voice)

        tempo : float
            Tempo of the score


        Returns
        -------
        score : symusic.Score object
            The score object on which you can call dump_midi to save it to a file

        """
        score = Score(ttype=self.tpq)
        score.tempos.append(Tempo(0, tempo))
        current_ts = None
        for chord in chords:
            ts = TimeSignature(chord[7], chord[5], chord[6])
            candidate_ts = (ts.numerator, ts.denominator)
            if current_ts != candidate_ts:
                score.time_signatures.append(ts)
                current_ts = (
                    (ts.numerator, ts.denominator) if current_ts is None else current_ts
                )

        for track_key in track_keys:
            idx, program, is_drum = track_key
            track = Track(program=program, is_drum=is_drum)
            track.notes = tracks[(idx, program, is_drum)]
            score.tracks.append(track)
        return score

    def _get_bars(self, score):
        """
        Get the bars of a score
        Parameters
        ----------
        score : symusic.Score object
            The score to get the bars from

        Returns
        -------
        bars : list
            List of tuples with the start and end time of each bar in ticks
        chord_durations: list
            List of tuples with the time signature of each bar

        """
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
            end_time, num, den = self._get_end_of_bar(
                time, time_signatures, ticks_per_quarter
            )
            chord_durations.append((num, den))
            bars.append((start_time, end_time))
            time = end_time
        return bars, chord_durations

    def _get_bar_nb_array_optimized(self, note_times, bars):
        """
        Get the bar number for each note in an optimized way
        Parameters
        ----------
        note_times : dict
            Dictionary with time key containing the note times
            
        bars : list
            List of tuples with the start and end time of each bar in ticks

        Returns
        -------
        bar_indices : np.array
            Array with the bar index for each note

        """
        # Convert bars to a NumPy array for efficient computation
        bars_array = np.array(bars)
        start_times = bars_array[:, 0]
        end_times = bars_array[:, 1]

        # Use broadcasting to find which bar each note belongs to
        # Note times are broadcast across the start and end times of bars to create a 2D boolean array
        in_bar = (note_times["time"][:, None] >= start_times) & (
            note_times["time"][:, None] < end_times
        )

        # Get the bar indices for each note. The result is a 2D array where each row has a single True value
        bar_indices = np.argmax(in_bar, axis=1)

        # Handle notes that do not fall within any bar by setting their bar index to a special value (e.g., -1)
        # This step is optional and depends on how you want to handle such cases
        outside_bars = ~in_bar.any(axis=1)
        bar_indices[outside_bars] = -1

        return bar_indices

    def _get_end_of_bar(self, bar_start, time_signatures, ticks_per_quarter):
        """
        Get the end of a bar given the start of the bar

        Parameters
        ----------
        bar_start : int
            The start of the bar in ticks
            
        time_signatures : list
            List of time signatures for the score

        ticks_per_quarter : int
            Ticks per quarter note for the midi file


        Returns
        -------
        end: int
            The end of the bar in ticks
        num: int
            The numerator of the time signature for the current bar
        den: int
            The denominator of the time signature for the current bar

        """
        # Find time signature
        # We use a tolrance of one quarter note to find the time signature
        res = [
            ts
            for ts in time_signatures
            if bar_start >= (ts.time - ticks_per_quarter // 2)
        ]
        time_signature = res[-1] if len(res) > 0 else TimeSignature(0, 4, 4)

        num = time_signature.numerator
        den = time_signature.denominator
        duration = 4 * frac(num, den)
        return int(bar_start + duration * ticks_per_quarter), num, den

    def _groupby_bar(self, score_soa, bars):
        """

        Parameters
        ----------
        score_soa :
            
        bars :
            

        Returns
        -------

        """
        # Group SOA by bar
        bar_nb_array = score_soa["bar"]
        # Time is relative to the start of the bar in our notation
        del score_soa["bar"]
        result = [
            {k: score_soa[k][bar_nb_array == bar_nb] for k in score_soa.keys()}
            for bar_nb in range(len(bars))
        ]
        return result

    def pprint(self, *text):
        """

        Parameters
        ----------
        *text :
            

        Returns
        -------

        """
        if self.verbose:
            print(*text)


    def _preload_score(self, midi_file):
        """
        Quantize the score to the desired tpq and min_dur

        Parameters
        ----------
        midi_file : str
            Path to the midi file to parse
            

        Returns
        -------
        score_quantized : symusic.Score object
            The quantized score object

        """

        score = symusic.Score(midi_file, ttype="tick")
        score_quantized = score.resample(tpq=self.tpq, min_dur=self.min_dur)
        return score_quantized

