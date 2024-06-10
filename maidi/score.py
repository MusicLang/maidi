from symusic import Track, TimeSignature, Note, Score, Tempo
from copy import deepcopy
import numpy as np
import os
import tempfile
import requests
import base64
import time

from maidi.constants import INSTRUMENTS_DICT, API_URL_VARIABLE, API_KEY_VARIABLE


class MidiScore:
    """
    The main object to handle midi scores. It allows to manipulate midi scores in a numpy-like way by splitting it
    into two dimensions : tracks and bars.

    **Usage**

    Load a midi file and write it to a new file

    >>> from maidi import MidiScore
    >>> score = MidiScore.from_midi("path/to/midi.mid")
    >>> score.write("path/to/output.mid")

    Add a track and assign the content of the track to be the same as the first track

    >>> from maidi import MidiScore
    >>> from maidi import instrument
    >>> score = MidiScore.from_midi("path/to/midi.mid")
    >>> score = score.add_instrument(instrument.ACOUSTIC_GUITAR)
    >>> score[-1, :] = score[0, :]

    Concatenate two scores horizontally

    >>> from maidi import MidiScore
    >>> score1 = MidiScore.from_midi("path/to/midi1.mid")
    >>> score2 = MidiScore.from_midi("path/to/midi2.mid")
    >>> score = score1.concatenate(score2, axis=1)


    """

    SCALE_DEGREE_INDEX = 0
    TONALITY_INDEX = 1
    MODE_INDEX = 2
    CHORD_OCTAVE_INDEX = 3
    CHORD_EXTENSION_INDEX = 4
    TIME_SIGNATURE_NUMERATOR_INDEX = 5
    TIME_SIGNATURE_DENOMINATOR_INDEX = 6
    FAKE_NOTE_VELOCITY = 1  # Should be < 2 to be ignored by the model
    FAKE_NOTE_DURATION = 2
    FAKE_NOTE_PITCH = 60

    def __init__(self, bars, tracks, track_keys, tempo, tpq=24, **kwargs):
        """
        Create a new MidiScore object, you usually never directly call the constructor.
        See :meth:`~MidiScore.from_midi()` or :meth:`~MidiScore.from_base64()` to create a new MidiScore object


        Parameters
        ----------

        bars : list of list
            List of bars in the score
        tracks : dict
            Dictionary of tracks in the score
        track_keys : list
            List of track keys
        tempo : int
            Tempo of the score
        tpq : int
            Ticks per quarter note
        kwargs : dict
            Additional arguments

        """
        self.bars = bars
        self.tracks = tracks
        self.track_keys = track_keys
        self.tempo = tempo
        self.tpq = tpq
        self.kwargs = kwargs

    @classmethod
    def from_midi(cls, midi_file, tpq=24, bar_range=None):
        """

        Parameters
        ----------
        midi_file :
            
        tpq :
             (Default value = 24)
        bar_range :
             (Default value = None)

        Returns
        -------

        """
        from maidi.parser import Parser

        parser = Parser(tpq=tpq)
        bars, tracks, track_keys, tempo = parser.parse(midi_file)
        score = cls(bars, tracks, track_keys, tempo, tpq=tpq)
        if bar_range is not None:
            score = score.get_score_between(*bar_range)
        return score

    @property
    def shape(self):
        """
        Return the shape of the score (n_tracks, n_bars)
        """
        return len(self.track_keys), len(self.bars)
    @property
    def nb_tracks(self):
        """
        Number of tracks (or instruments) in the score
        """
        return len(self.track_keys)

    @classmethod
    def from_base64(cls, base64_string, tpq=24):
        """Create a score from a base64 string

        Parameters
        ----------
        base64_string :
            str, base64 string
        tpq :
            int, ticks per quarter note (Default value = 24)

        Returns
        -------

        """
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=True) as midi_file:
            midi_file.write(base64.b64decode(base64_string))
            midi_file.flush()
            score = cls.from_midi(midi_file.name, tpq=tpq)
        return score


    def __getitem__(self, item):
        """
        Get the subscore corresponding to the items like the score was a matrix.
        Query in the numpy style
        The only difference is that all query will output an object of the same number of dimensions as the original object (A score)


        Parameters
        ----------

        item : int, slice or tuple
            The index or slice of the score to get
            If a tuple is provided, the first element is the track index and the second element is the bar index

        Returns
        -------
        score: MidiScore
            The subscore corresponding to the query

        """
        score = self
        if isinstance(item, tuple):
            first_dim, second_dim = item
            subtrack_score = score.get_tracks(first_dim)
            return subtrack_score.get_bars(second_dim)

        if isinstance(item, (slice, int)):
            return score.get_tracks(item)

    def concatenate(self, other_score, axis=0):
        """
        Concatenate two scores along a specific axis (0 = horizontally, 1 = vertically)

        For 0 axis concatenation, the number of tracks must be the same, the bars from left score are kept
        For 1 axis concatenation, the number of bars must be the same, the tracks from the left score are kept

        Parameters
        ----------

        other_score : MidiScore
            The score to concatenate with
        axis : int (Default value = 0)
            The axis along which to concatenate (0 = horizontally, 1 = vertically)

        """
        # Check shapes are compatible
        if axis == 0:
            if self.nb_bars != other_score.nb_bars:
                raise ValueError("The number of bars must be the same for axis 0 concatenation")
            new_score = self.copy()
            nb_tracks_to_add = len(other_score.track_keys)
            for track_key in other_score.track_keys:
                new_score = new_score.add_track(track_key[1], track_key[2])
            new_score[-nb_tracks_to_add:, :] = other_score.copy()
            return new_score

        if axis == 1:
            right_bars = deepcopy(other_score.bars)
            if self.nb_tracks != other_score.nb_tracks:
                raise ValueError("The number of tracks must be the same for axis 1 concatenation")
            new_score = self.copy().add_silence_bars(len(right_bars))
            new_score[:, -len(right_bars):] = other_score.copy()
            # bars should be set to second score
            new_score.bars = self.bars + right_bars
            return new_score

    def normalize_track_indexes(self):
        """
        Normalize the track indexes to be in the range of the number of tracks
        """
        score = self.copy()
        new_track_keys = []
        track_mapping = {}
        for real_track_idx, track_key in enumerate(score.track_keys):
            track_mapping[track_key] = (real_track_idx, *track_key[1:])
            new_track_keys.append((real_track_idx, *track_key[1:]))
        score.track_keys = new_track_keys
        new_tracks = {}
        for track_key, track in score.tracks.items():
            new_tracks[track_mapping[track_key]] = track
        score.tracks = new_tracks
        return score

    def __setitem__(self, item, value):
        """
        Set the subscore corresponding to the items like the score was a matrix.
        Set in the numpy style
        The only difference is that all query will output an object of the same number of dimensions as the original object (A score)

        Parameters
        ----------
        item : int, slice or tuple
            The index or slice of the score to get
            If a tuple is provided, the first element is the track index and the second element is the bar index
        value : MidiScore
            The subscore to set, should have the same shape as the query

        Returns
        -------
        None
        """
        if not isinstance(value, MidiScore):
            raise TypeError("Value must be a MidiScore instance")

        if isinstance(item, int):
            # Single integer index implies updating a specific track across all tracks
            track_indexes = [item]

            # Ensure the value has the same structure
            if len(value.shape[0]) != 1:
                raise ValueError("The provided MidiScore must have one track")
            if len(value.shape[1]) != len(self.bars):
                raise ValueError("The provided MidiScore must have the same number of bars")

            # Update the track notes
            self.assign_tracks(track_indexes, value)

        elif isinstance(item, slice):
            start, end = item.start, item.stop
            if start is None and end is None:
                return value
            start = start if start is not None else 0
            end = end if end is not None else len(self.track_keys)

            if start < 0:
                start = len(self.track_keys) + start
            if end < 0:
                end = len(self.track_keys) + end + 1

            track_indexes = range(start, end)
            self.assign_tracks(track_indexes, value)

        if isinstance(item, tuple):

            first_dim, second_dim = item
            if isinstance(first_dim, int):
                first_dim = slice(first_dim, first_dim + 1 if first_dim + 1 != 0 else None )
            if isinstance(second_dim, int):
                second_dim = slice(second_dim, second_dim + 1 if second_dim + 1 != 0 else None)

            start_first_dim = first_dim.start if first_dim.start is not None else 0
            end_first_dim = first_dim.stop if first_dim.stop is not None else len(self.track_keys)
            start_second_dim = second_dim.start if second_dim.start is not None else 0
            end_second_dim = second_dim.stop if second_dim.stop is not None else len(self.bars)

            if start_first_dim < 0:
                start_first_dim = len(self.track_keys) + start_first_dim
            if start_second_dim < 0:
                start_second_dim = len(self.bars) + start_second_dim
            if end_first_dim < 0:
                end_first_dim = len(self.track_keys) + end_first_dim + 1
            if end_second_dim < 0:
                end_second_dim = len(self.bars) + end_second_dim + 1

            receiver_shape = (end_first_dim - start_first_dim, end_second_dim - start_second_dim)
            value_shape = value.shape
            if receiver_shape != value_shape:
                raise ValueError(f"Shapes do not match: {receiver_shape} != {value_shape}")

            self.assign_tracks(range(start_first_dim, end_first_dim), value, bar_range=(start_second_dim, end_second_dim))

        else:
            raise TypeError("Index must be an int or a tuple of two ints")

    def __iter__(self):
        return iter(self.track_keys)

    def __len__(self):
        return len(self.track_keys)

    def assign_tracks(self, track_indexes, other_score, bar_range=None):
        """
        Assign some tracks of the other_score to the current score
        """
        # Update the track notes
        for idx, track_index in enumerate(track_indexes):
            value_track = other_score.track_keys[idx]
            self_track = self.track_keys[track_index]
            if bar_range is None:
                for bar_idx in range(len(self.bars)):
                    self.tracks[self_track][bar_idx] = other_score.tracks[value_track][bar_idx]
            else:
                for abs_idx, bar_idx in enumerate(range(*bar_range)):
                    self.tracks[self_track][bar_idx] = other_score.tracks[value_track][abs_idx]

    def get_track_from_index(self, index):
        return self.tracks[self.track_keys[index]]

    def get_track_bar(self, idx_track, idx_bar):
        return self.tracks[self.track_keys[idx_track]][idx_bar]

    def get_chords_prompt(self):
        """
        Return the list of chords in the score in the format [(chord_degree, tonality, mode, chord extension), ...]

        Chord degree : int, degree of the chord in the tonality but 0 indexed (0-6), tonic is 0, fifth is 4
        Tonality : int, tonality in which the chord is played (0-11), 0 is C, 1 is C#, 2 is D, ...
        Mode : str, mode of the tonality, "m" for minor, "M" for major
        Chord extension : str, extension of the chord as in roman numeral notation, in ['', ',6', '64', '7', '65', '43', '2']
        Optionally you can use (sus2) or (sus4) for suspended chords

        Returns
        -------
        chords: list of tuple
        As specified above

        """
        kept_indexes = [self.SCALE_DEGREE_INDEX, self.TONALITY_INDEX, self.MODE_INDEX, self.CHORD_EXTENSION_INDEX]
        return [[bar[index] for index in kept_indexes] for bar in self.bars]
    def get_bars(self, item):
        """
        Get the bars between the start and end index

        slice: int or Slice, slice object
        """
        if isinstance(item, int):
            item = slice(item, item + 1 if item + 1 != 0 else None)
        start, end = item.start, item.stop

        if start is None and end is None:
            return self

        return self.get_score_between(start, end)


    def add_note(self, pitch, time, duration, velocity , track_index, bar_index):
        """Add a note to the score

        Parameters
        ----------
        pitch :
            int, pitch of the note
        velocity :
            int, velocity of the note
        duration :
            int, duration of the note
        track_index :
            int, index of the track
        bar_index :
            int, index of the bar
        time :
            int, time of the note

        Returns
        -------

        """
        score = self
        track_key = score.track_keys[track_index]
        score.tracks[track_key][bar_index]["time"] = np.append(score.tracks[track_key][bar_index]["time"], time)
        score.tracks[track_key][bar_index]["pitch"] = np.append(score.tracks[track_key][bar_index]["pitch"], pitch)
        score.tracks[track_key][bar_index]["duration"] = np.append(score.tracks[track_key][bar_index]["duration"], duration)
        score.tracks[track_key][bar_index]["velocity"] = np.append(score.tracks[track_key][bar_index]["velocity"], velocity)
        return score

    def get_tracks(self, item):
        """
        Get the tracks between the start and end index

        slice: int or Slice, slice object
        """
        if isinstance(item, int):
            item = slice(item, item + 1 if item + 1 != 0 else None)
        start, end = item.start, item.stop

        if start is None and end is None:
            return self

        return self.get_track_subset(start, end)


    def to_base64(self):
        """Transform the score to a base64 string
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=True) as midi_file:
            self.write(midi_file.name)
            with open(midi_file.name, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode()
        # Remove the temporary file
        return encoded_string

    def delete_bar(self, bar_index):
        """Delete a bar from the score

        Parameters
        ----------
        bar_index :
            int, index of the bar to delete

        Returns
        -------

        """
        score = self.copy()
        new_bars = deepcopy(score.bars)
        new_tracks = deepcopy(score.tracks)

        for track_key in score.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)].pop(bar_index)

        return MidiScore(new_bars, new_tracks, score.track_keys, score.tempo, score.tpq).normalize_track_indexes()

    @classmethod
    def _get_fake_note_vector(cls):
        """ """
        return {
            "time": np.asarray([0], dtype=np.int32),
            "pitch": np.asarray([cls.FAKE_NOTE_PITCH], dtype=np.int8),
            "duration": np.asarray([cls.FAKE_NOTE_DURATION], dtype=np.int32),
            "velocity": np.asarray([cls.FAKE_NOTE_VELOCITY], dtype=np.int8),
        }


    @classmethod
    def _get_bar_duration_from_bar(cls, bar, tpq):
        return int(bar[cls.TIME_SIGNATURE_NUMERATOR_INDEX] * 4 * tpq / bar[cls.TIME_SIGNATURE_DENOMINATOR_INDEX])

    def get_bar_duration(self, bar_index):
        """
        Get the duration of a bar in ticks for a specific bar of the score

        Parameters
        ----------
        bar_index : int
            Index of the bar



        Returns
        -------
        int
            Duration of the bar in ticks

        """
        return self._get_bar_duration_from_bar(self.bars[bar_index], self.tpq)

    @classmethod
    def _get_bar_start_end_tick_from_bars(cls, bars, bar_index, tpq):
        """
        Calculate the start and end tick of a given bar on a score

        """
        time = 0
        for temp_bar_idx, bar in enumerate(bars[:bar_index]):
            bar_duration = cls._get_bar_duration_from_bar(bar, tpq)
            time += bar_duration
        start = time
        end = time + cls._get_bar_duration_from_bar(bars[bar_index], tpq)

        return start, end

    def get_bar_start_end_tick(self, bar_index):
        """
        Calculate the start and end tick of a given bar on the score

        Parameters
        ----------
        bar_index :  int
            Index of the bar


        Returns
        -------
        start: int
            Start tick of the bar
        end: int
            End tick of the bar


        """
        return self._get_bar_start_end_tick_from_bars(self.bars, bar_index, self.tpq)

    def notes_to_note_tick_list(self, notes, bars):
        """

        Parameters
        ----------
        notes :
            
        bars :
            

        Returns
        -------

        """
        note_tick_list = []
        for idx, (bar, note_list) in enumerate(zip(bars, notes)):
            bar_start, bar_end = self.get_bar_start_end_tick(idx)
            for note in note_list:

                note_tick_list.append(
                    (
                        note.start,
                        note.end,
                        note.pitch,
                        bar[self.TIME_SIGNATURE_NUMERATOR_INDEX],
                        bar[self.TIME_SIGNATURE_DENOMINATOR_INDEX],
                        bar_start,
                        bar_end,
                        idx,
                    )
                )
        return note_tick_list

    def write(self, filename):
        """

        Parameters
        ----------
        filename :
            

        Returns
        -------

        """
        score = Score(self.tpq)
        score.tempos.append(Tempo(0, self.tempo))
        current_ts = None
        for index_bar, bar in enumerate(self.bars):
            start_bar, end_bar = self.get_bar_start_end_tick(index_bar)
            ts = TimeSignature(
                start_bar,
                bar[self.TIME_SIGNATURE_NUMERATOR_INDEX],
                bar[self.TIME_SIGNATURE_DENOMINATOR_INDEX],
            )
            candidate_ts = (ts.numerator, ts.denominator)
            if current_ts != candidate_ts:
                score.time_signatures.append(ts)
                current_ts = (
                    (ts.numerator, ts.denominator) if current_ts is None else current_ts
                )

        for track_key in self.track_keys:
            idx, program, is_drum = track_key
            track = Track(program=program, is_drum=is_drum)
            track.notes = self.track_notes_to_score_notes(
                self.bars, self.tracks[(idx, program, is_drum)], self.tpq
            )
            score.tracks.append(track)

        score.dump_midi(filename)
        return score

    @classmethod
    def track_notes_to_score_notes(cls, bars, track_notes, tpq):
        """

        Parameters
        ----------
        bars :
            
        track_notes :
            

        Returns
        -------

        """
        notes = []
        has_note = False
        for idx_bar, bar_track_notes in enumerate(track_notes):
            start_bar_tick, end_bar_tick = cls._get_bar_start_end_tick_from_bars(bars, idx_bar, tpq=tpq)
            for idx in range(len(bar_track_notes["time"])):
                time = (
                    bar_track_notes["time"][idx]
                    + start_bar_tick
                )
                pitch = bar_track_notes["pitch"][idx]
                duration = bar_track_notes["duration"][idx]
                velocity = bar_track_notes["velocity"][idx]
                notes.append(Note(time, duration, pitch, velocity))
                has_note = True
        if not has_note:
            notes.append(
                Note(
                    0,
                    cls.FAKE_NOTE_DURATION,
                    cls.FAKE_NOTE_PITCH,
                    cls.FAKE_NOTE_VELOCITY,
                )
            )
        return notes

    @staticmethod
    def offset_notes(offset, tracks, track_keys):
        """

        Parameters
        ----------
        offset :
            
        tracks :
            
        track_keys :
            

        Returns
        -------

        """
        new_tracks = {}
        for track_key in track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)] = deepcopy(
                tracks[(idx, program, is_drum)]
            )
            for notes in new_tracks[(idx, program, is_drum)]:
                notes["time"] = (
                    np.asarray(notes["time"].copy(), dtype=np.int32) + offset
                )
                assert all(
                    [time >= 0 for time in notes["time"]]
                ), f"Negative time found in track {track_key}"

        return new_tracks

    def offset_score(self, offset):
        """

        Parameters
        ----------
        offset :
            

        Returns
        -------

        """
        new_bars = deepcopy(self.bars)

        return MidiScore(
            new_bars,
            deepcopy(self.tracks),
            deepcopy(self.track_keys),
            self.tempo,
            self.tpq,
        )

    def get_score_between(self, start_bar, end_bar):
        """

        Parameters
        ----------
        start_bar :
            
        end_bar :
            

        Returns
        -------

        """

        new_bars = deepcopy(self.bars[start_bar:end_bar])
        if start_bar is None:
            start_bar = 0


        new_tracks = {}
        for track_key in self.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)] = self.tracks[
                (idx, program, is_drum)
            ][start_bar:end_bar]
            assert len(new_tracks[(idx, program, is_drum)]) == len(
                new_bars
            ), "Track and bar length mismatch"
        return MidiScore(new_bars, new_tracks, self.track_keys, self.tempo, self.tpq)

    def copy(self):
        """ """
        return MidiScore(
            deepcopy(self.bars),
            deepcopy(self.tracks),
            deepcopy(self.track_keys),
            self.tempo,
            self.tpq,
        )

    def get_mask(self):
        """Get the mask of the score (np.array of shape (n_tracks, n_bars))
        The mask allows to specify which bar of the score should be regenerated by a model (ones)
        The mask is the same size as the score and is empty by default (all zeros)

        Parameters
        ----------

        Returns
        -------
        mask: np.array of shape (n_tracks, n_bars)
            Mask of the score, empty by default (all zeros)

        """
        import numpy as np

        mask = np.zeros((len(self.track_keys), len(self.bars)))

        return mask

    def get_empty_controls(self, prevent_silence=False):
        """Get the mask, the tags and the bars of the current score.
        The mask is a np.array of shape (n_tracks, n_bars)
        The tags is a list of list of list of size (n_tracks, n_bars, <variable size>)
        The bars is a list of size (n_bars,)

        Parameters
        ----------
        prevent_silence :
            bool, if True add a tag to each bar to explicitly prevent silence during generation (Default value = False)

        Returns
        -------

        """
        mask = self.get_mask()
        tags = [[[] for _ in range(mask.shape[1])] for _ in range(mask.shape[0])]
        tags = self.prevent_silence_tags(tags) if prevent_silence else tags
        bars = [None for _ in range(mask.shape[1])]
        return mask, tags, bars

    @classmethod
    def prevent_silence_tags(self, tags):
        """Prevent silence tags from being added to the tags

        Parameters
        ----------
        tags :
            list of list of list of str, tags to prevent silence

        Returns
        -------

        """
        for i in range(len(tags)):
            for j in range(len(tags[i])):
                if not tags[i][j]:
                    tags[i][j].append("CONTROL_MIN_POLYPHONY__1")
        return tags

    @property
    def nb_bars(self):
        """ """
        return len(self.bars)

    def get_track_subset(self, start, end):
        """

        Parameters
        ----------
        start :
            
        end :
            

        Returns
        -------

        """
        score = self.copy()
        score.track_keys = score.track_keys[start:end]
        score.tracks = {
            track_key: score.tracks[track_key] for track_key in score.track_keys
        }
        return score

    def get_silenced_mask(self):
        """

        Parameters
        ----------

        Returns
        -------
        type
            :return:

        """
        mask = np.zeros((len(self.track_keys), len(self.bars)))
        for i, track_key in enumerate(self.track_keys):
            idx, program, is_drum = track_key
            for j, bar in enumerate(self.bars):
                mask[i, j] = (
                    self.tracks[(idx, program, is_drum)][j]["pitch"].shape[0]
                    == 0
                )
        return mask

    def get_silenced_bars(self):
        """ """
        silenced_mask = self.get_silenced_mask()
        silenced_bars = np.all(silenced_mask == 1, axis=0)
        return silenced_bars

    def cut_silenced_bars_at_beginning_and_end(self):
        """Cut silenced bars at the beginning and end of the score
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        score = self.copy()
        silenced_bars = score.get_silenced_bars()
        # Cut silenced bars at the beginning
        bar_to_cut_start = 0
        while silenced_bars[bar_to_cut_start]:
            bar_to_cut_start += 1
            if bar_to_cut_start == len(silenced_bars):
                break

        # Cut silenced bars at the end
        bar_to_cut_end = 0
        while silenced_bars[-bar_to_cut_end - 1]:
            bar_to_cut_end += 1
            if bar_to_cut_end == len(silenced_bars):
                break
        score = score.get_score_between(
            bar_to_cut_start, len(score.bars) - bar_to_cut_end
        )
        return score

    def check_mask(self, mask):
        """Check that the mask is valid

        Parameters
        ----------
        mask :
            np.array of shape (n_tracks, n_bars)

        Returns
        -------

        """
        if mask.shape[1] != len(self.bars):
            raise ValueError(
                f"Mask length does not match score length {mask.shape[1]} != {len(self.bars)}"
            )
        if mask.shape[1] > 16:
            raise ValueError("Mask length must be less than 16")
        if mask.shape[0] != len(self.track_keys):
            raise ValueError(
                "Mask number of tracks does not match score number of tracks"
            )

    def check_times(self):
        """ """
        for track_key in self.track_keys:
            idx, program, is_drum = track_key
            assert len(self.tracks[(idx, program, is_drum)]) == len(
                self.bars
            ), "Track and bar length mismatch"

    def sanitize_score(self, score_to_compare, mask):
        """Do checks after predicting a score

        Parameters
        ----------
        score :
            param score_to_compare:
        mask :
            return:
        score_to_compare : MidiScore


        Returns
        -------

        """
        score = self.copy()
        score.check_times()
        if len(score.track_keys) > len(score_to_compare.track_keys):
            # If the model added tracks, we need to remove them
            score = score.get_track_subset(0, len(score_to_compare.track_keys))

        if score.nb_bars < mask.shape[1]:
            pass
            # score = score.add_silence_bars(mask.shape[1] - score.nb_bars, add_fake_notes=True)
        if score.nb_bars > mask.shape[1]:
            score = score.get_score_between(0, mask.shape[1])

        return score

    def cut_notes_to_end_of_bars(self):
        """Cut durations of notes that go beyond the end of the bar
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self = self.copy()
        new_tracks = {}
        for track_key in self.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)] = deepcopy(
                self.tracks[(idx, program, is_drum)]
            )
            for idx_bar, bar in enumerate(self.bars):
                bar_start, bar_end = self.get_bar_start_end_tick(idx_bar)
                bar_duration = bar_end - bar_start
                for idx_note, note in enumerate(
                    new_tracks[(idx, program, is_drum)][idx_bar]["time"]
                ):
                    if (
                        note
                        + new_tracks[(idx, program, is_drum)][idx_bar][
                            "duration"
                        ][idx_note]
                        > bar_duration
                    ):
                        new_tracks[(idx, program, is_drum)][idx_bar][
                            "duration"
                        ][idx_note] = (bar_duration - note)

        return MidiScore(
            deepcopy(self.bars),
            new_tracks,
            deepcopy(self.track_keys),
            self.tempo,
            self.tpq,
        )

    def add_instrument(self, instrument):
        try:
            program, is_drum = INSTRUMENTS_DICT[instrument]
        except KeyError:
            raise ValueError(f"Unknown instrument {instrument}")

        return self.add_track(program, is_drum)

    def add_track(self, program, is_drum):
        """Add an empty track (with fake notes) to the score

        Parameters
        ----------
        program :
            int, program number
        is_drum :
            bool, is drum track

        Returns
        -------

        """
        self = self.copy()
        max_track_index = max([track_key[0] for track_key in self.track_keys])
        new_track_key = (max_track_index+1, program, bool(is_drum))
        self.track_keys.append(new_track_key)
        self.tracks[new_track_key] = [
            self._get_fake_note_vector() for _ in range(len(self.bars))
        ]
        return self.normalize_track_indexes()

    @classmethod
    def match_track_keys(cls, score, other_score):
        """Match the track keys of two scores
        First find the midi with the most tracks
        Assert shortest score tracks match the beginning of the longest score tracks
        Then add fake tracks to the shortest score
        And returns both tracks in the same order

        Parameters
        ----------
        other_score :
            MidiScore, Score on which to match track keys
        score :
            

        Returns
        -------

        """
        score = score.copy()
        other_score = other_score.copy()

        if score.track_keys == other_score.track_keys:
            return score, other_score

        first_longer = len(score.track_keys) > len(other_score.track_keys)
        if first_longer:
            longer_score = score
            shorter_score = other_score
        else:
            longer_score = other_score
            shorter_score = score

        # Assert that the shorter score tracks match the beginning of the longer score tracks
        for i, track_key in enumerate(shorter_score.track_keys):
            if track_key != longer_score.track_keys[i]:
                raise ValueError(
                    "Score A and B have totally different tracks, cannot match them"
                )
        # Add fake tracks to the shorter score
        for i in range(len(shorter_score.track_keys), len(longer_score.track_keys)):
            shorter_score = shorter_score.add_track(
                longer_score.track_keys[i][1], longer_score.track_keys[i][2]
            )

        return score, other_score

    def change_instrument(self, track_idx, instrument):
        """Change the instrument of a track

        Parameters
        ----------
        track_idx :
            param instrument:
        instrument :
            

        Returns
        -------

        """
        score = self.copy()
        track_key = score.track_keys[track_idx]
        new_track_index = (
            track_key[0],
            INSTRUMENTS_DICT[instrument][0],
            bool(INSTRUMENTS_DICT[instrument][1]),
        )
        score.track_keys[track_idx] = new_track_index
        # Change in tracks
        score.tracks[new_track_index] = score.tracks.pop(track_key)
        return score

    def add(self, other_score, silence_bars=0, try_matching_tracks=True):
        """Concatenate the current score with another score horizontally

        Parameters
        ----------
        other_score :
            MidiScore
        silence_bars :
            int, number of silence bars to add between the two scores (Default value = 0)
        try_matching_tracks :
            bool, if True try to match the tracks of the two scores (Default value = True)

        Returns
        -------

        """
        score = self.copy()
        if silence_bars > 0:
            initial_length = len(score.bars)
            score = score.add_silence_bars(silence_bars, add_fake_notes=False)
            assert (
                len(score.bars) == initial_length + silence_bars
            ), "Silence bars not added correctly"
        other_score = other_score.copy()
        # Assert that the other score has the same tracks
        if other_score.track_keys != score.track_keys:
            if try_matching_tracks:
                score, other_score = self.match_track_keys(score, other_score)
            else:
                raise ValueError("Track keys do not match")
        # Offset the other score to start after the current score
        new_bars = score.bars + other_score.bars
        new_tracks = {}
        for track_key in score.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)] = (
                score.tracks[(idx, program, is_drum)]
                + other_score.tracks[(idx, program, is_drum)]
            )
        return MidiScore(
            new_bars, new_tracks, score.track_keys, score.tempo, score.tpq
        )

    def add_silence_bars(self, n_bars, add_fake_notes=True):
        """Add n_bars of silence to the end of the score

        Parameters
        ----------
        n_bars :
            int, number of silence bars to add
        add_fake_notes :
            bool, if True add a fake note to each track (Default value = True)

        Returns
        -------

        """
        score = self.copy()
        # Assert that the other score has the same tracks
        # Offset the other score to start after the current score
        if n_bars <= 0:
            raise ValueError(
                "n_bars must be positive"
            )  # If we want to add silence bars

        new_bars = score.bars
        for i in range(n_bars):
            new_bars.append(deepcopy(score.bars[-1]))

        new_tracks = {}
        for track_key in score.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)] = score.tracks[
                (idx, program, is_drum)
            ]
            for new_bar in new_bars[-n_bars:]:
                if add_fake_notes:
                    new_tracks[(idx, program, is_drum)].append(
                        self._get_fake_note_vector()
                    )
                else:
                    new_tracks[(idx, program, is_drum)].append(
                        {
                            "time": np.asarray([], dtype=np.int32),
                            "pitch": np.asarray([], dtype=np.int8),
                            "duration": np.asarray([], dtype=np.int32),
                            "velocity": np.asarray([], dtype=np.int8),
                        }
                    )
            # Assert good length
            assert len(new_tracks[(idx, program, is_drum)]) == len(
                new_bars
            ), "Track and bar length mismatch"
        return MidiScore(
            new_bars, new_tracks, score.track_keys, score.tempo, score.tpq
        )

    @classmethod
    def from_empty(cls, instruments, nb_bars, ts=(4, 4), tempo=120, tpq=24):
        """

        Parameters
        ----------
        instruments :
            
        nb_bars :
            
        ts :
             (Default value = (4)
        4) :
            
        tempo :
             (Default value = 120)
        tpq :
             (Default value = 24)

        Returns
        -------

        """
        bar_duration_quarters = 4 * ts[0] / ts[1]
        track_keys = [
            (idx, INSTRUMENTS_DICT[ins][0], INSTRUMENTS_DICT[ins][1] == 1)
            for idx, ins in enumerate(instruments)
        ]
        bars = [
            [
                0,
                0,
                "M",
                0,
                "",
                ts[0],
                ts[1],
                int(i * tpq * bar_duration_quarters),
                int((i + 1) * tpq * bar_duration_quarters),
            ]
            for i in range(nb_bars)
        ]
        assert len(bars) == nb_bars, "Bars length mismatch"
        tracks = {}
        for track_key in track_keys:
            tracks[track_key] = [cls._get_fake_note_vector() for _ in range(nb_bars)]

            assert len(tracks[track_key]) == nb_bars, "Track and bar length mismatch"

        return cls(bars, tracks, track_keys, tempo, tpq=tpq)
