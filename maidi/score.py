from symusic import Track, TimeSignature, Note, Score, Tempo
from copy import deepcopy
import numpy as np
import os
import tempfile
import requests
import base64
import time

from maidi.constants import INSTRUMENTS_DICT, API_URL_VARIABLE, MUSICLANG_API_KEY_VARIABLE


class MidiScore:
    """
    The main object to handle midi scores. It allows to manipulate midi scores in a numpy-like way by splitting it
    into two dimensions : tracks and bars.

    warning :: All midi notes with velocity < 2 are ignored when writing midi files, they are considered as fake notes. This behaviour will be removed in the future

    warning:: This class should not be directly instantiated, use :meth:`~MidiScore.from_midi()` or :meth:`~MidiScore.from_base64()` instead

    **Usage**

    Load a midi file and write it to a new file

    >>> from maidi import MidiScore
    >>> score = MidiScore.from_midi("path/to/midi.mid")
    >>> score.write("path/to/output.mid")

    Add a track and assign the content of the track to be the same as the first track

    >>> from maidi import MidiScore, instrument
    >>> score = MidiScore.from_midi("path/to/midi.mid")
    >>> score = score.add_instrument(instrument.ACOUSTIC_GUITAR)
    >>> score[-1, :] = score[0, :]

    Concatenate two scores horizontally

    >>> from maidi import MidiScore
    >>> score1 = MidiScore.from_midi("path/to/midi1.mid")
    >>> score2 = MidiScore.from_midi("path/to/midi2.mid")
    >>> score = score1.concatenate(score2, axis=1)
    >>> score.nb_bars == score1.nb_bars + score2.nb_bars
    True


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
    MINIMUM_VELOCITY = 2
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
    def from_midi(cls, midi_file, tpq=24, bar_range=None, force_ts=None):
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
        bars, tracks, track_keys, tempo = parser.parse(midi_file, force_ts=force_ts)
        score = cls(bars, tracks, track_keys, tempo, tpq=tpq)

        if bar_range is not None:
            score = score.get_score_between(*bar_range)
        return score

    def cut_silence_bars_at_end(self):
        """
        Cut the silence bars at the end of the score
        """
        score = self.copy()
        while score.is_bar_empty(-1, keep_ghost_note=True):
            score = score.delete_bar(-1)
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


    @classmethod
    def concatenate_scores(cls, scores, axis=0):
        """
        Concatenate multiple scores along a specific axis (0 = horizontally, 1 = vertically)

        For 0 axis concatenation, the number of tracks must be the same, the bars from left score are kept
        For 1 axis concatenation, the number of bars must be the same, the tracks from the left score are kept

        Parameters
        ----------

        scores : list
            List of scores to concatenate with
        axis : int (Default value = 0)
            The axis along which to concatenate (0 = horizontally, 1 = vertically)

        Returns
        -------
        MidiScore
            The concatenated score

        """
        if axis == 0:
            if len(scores) == 0:
                raise ValueError("No score to concatenate")
            new_score = scores[0].copy()
            for score in scores[1:]:
                new_score = new_score.concatenate(score, axis=0)
            return new_score

        if axis == 1:
            if len(scores) == 0:
                raise ValueError("No score to concatenate")
            new_score = scores[0].copy()
            for score in scores[1:]:
                new_score = new_score.concatenate(score, axis=1)
            return new_score

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
            if self.nb_tracks == 0:
                return other_score.copy()
            if other_score.nb_tracks == 0:
                return self.copy()
            if self.nb_bars != other_score.nb_bars:
                raise ValueError("The number of bars must be the same for axis 0 concatenation")
            new_score = self.copy()
            nb_tracks_to_add = len(other_score.track_keys)
            for track_key in other_score.track_keys:
                new_score = new_score.add_track(track_key[1], track_key[2])
            new_score[-nb_tracks_to_add:, :] = other_score.copy()
            return new_score

        if axis == 1:
            if self.nb_bars == 0:
                return other_score.copy()
            if other_score.nb_bars == 0:
                return self.copy()

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
            if value.shape[0] != 1:
                raise ValueError("The provided MidiScore must have one track")
            if value.shape[1] != len(self.bars):
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

            nb_tracks = end - start
            if value.shape[0] != nb_tracks:
                raise ValueError(f"The provided MidiScore must have the same number of tracks assigned : ({value.shape[0]}) != self : ({nb_tracks})")

            if value.shape[1] != self.shape[1]:
                raise ValueError(f"The provided MidiScore must have the same number of bars assigned : ({value.shape[1]}) != self : ({self.shape[1]}) ")

            track_indexes = range(start, end)
            self.assign_tracks(track_indexes, value)

        elif isinstance(item, tuple):

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
                end_first_dim = len(self.track_keys) + end_first_dim
            if end_second_dim < 0:
                end_second_dim = len(self.bars) + end_second_dim

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

    def is_bar_empty(self, bar_index, keep_ghost_note=False):
        """
        Check if a bar is empty

        Parameters
        ----------
        bar_index : int
            Index of the bar to check
        keep_ghost_note : bool
            If True, ghost note counts as note in the check

        """
        return all(self.is_bar_track_empty(track_index, bar_index, keep_ghost_note=keep_ghost_note) for track_index in range(self.nb_tracks))


    def is_bar_track_empty(self, track_index, bar_index, keep_ghost_note=False):
        """
        Check if a bar is empty

        Parameters
        ----------
        track_index : int
            Index of the track
        bar_index : int
            Index of the bar to check
        keep_ghost_note : bool
            If True, ghost note counts as note in the check

        """
        no_notes = len(self.tracks[self.track_keys[track_index]][bar_index]["time"]) == 0
        if not no_notes:
            if not keep_ghost_note:
                only_ghost_notes = self.tracks[self.track_keys[track_index]][bar_index]["velocity"].max() < self.MINIMUM_VELOCITY
                if only_ghost_notes:
                    return True
        else:
            return True

        return False


    def get_chord_manager(self, use_last_chord_for_silence=True):
        """
        Return a chord manager from the chords of the score

        Parameters
        ----------
        use_last_chord_for_silence : bool
            If True, use the last chord played for silenced bars, otherwise return None


        Returns
        -------
        cm: ChordManager

        """
        from maidi import ChordManager
        chords = self.get_chords(use_last_chord_for_silence=use_last_chord_for_silence)
        return ChordManager(chords)

    def get_chords(self, use_last_chord_for_silence=True):
        """
        Return the list of chords in the score in the format [(chord_degree, tonality, mode, chord extension), ...]

        Chord degree : int, degree of the chord in the tonality but 0 indexed (0-6), tonic is 0, fifth is 4
        Tonality : int, tonality in which the chord is played (0-11), 0 is C, 1 is C#, 2 is D, ...
        Mode : str, mode of the tonality, "m" for minor, "M" for major
        Chord extension : str, extension of the chord as in roman numeral notation, in ['', ',6', '64', '7', '65', '43', '2']
        Optionally you can use (sus2) or (sus4) for suspended chords

        Parameters
        ----------
        use_last_chord_for_silence : bool
            If True, use the last chord played for silenced bars, otherwise return None


        Returns
        -------
        chords: list of tuple
        As specified above

        """
        kept_indexes = [self.SCALE_DEGREE_INDEX, self.TONALITY_INDEX, self.MODE_INDEX, self.CHORD_EXTENSION_INDEX]
        chords = []
        last_chord = (0, 0, "M", "")
        for bar in range(len(self.bars)):
            chord = tuple([self.bars[bar][idx] for idx in kept_indexes])
            if self.is_bar_empty(bar):
                if use_last_chord_for_silence:
                    chord = last_chord
                else:
                    chord = (0, 0, "M", "")
            chords.append(chord)
            last_chord = chord
        return chords

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
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as midi_file:
                temp_file_name = midi_file.name
                self.write(temp_file_name)

            # Open the temporary file for reading
            with open(temp_file_name, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode()

            # Remove the temporary file
            os.remove(temp_file_name)

            return encoded_string
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

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
        new_bars.pop(bar_index)
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
    def _get_empty_note_vector(cls):
        """ """
        return {
            "time": np.asarray([], dtype=np.int32),
            "pitch": np.asarray([], dtype=np.int8),
            "duration": np.asarray([], dtype=np.int32),
            "velocity": np.asarray([], dtype=np.int8),
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
                    (ts.numerator, ts.denominator)
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

    def get_empty_controls(self, prevent_silence=True):
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
        chords = [None for _ in range(mask.shape[1])]
        return mask, tags, chords

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


    def cut_notes_at_the_end(self, only_end=True):
        """
        On last bar, cut duration of note if it goes after the bar duration

        Parameters
        ----------
        only_end : boolean
            Only cut the last bar (Default value = True)

        """
        score = self.copy()
        for track_key in score.track_keys:
            idx, program, is_drum = track_key
            if not only_end:
                selected_range = range(len(score.bars))
            else:
                selected_range = [len(score.bars) - 1]
            for bar_idx in selected_range:
                bar_duration = score.get_bar_duration(bar_idx)
                for note_idx in range(len(score.tracks[track_key][bar_idx]["time"])):
                    note_duration = score.tracks[track_key][bar_idx]["duration"][note_idx]
                    note_time = score.tracks[track_key][bar_idx]["time"][note_idx]
                    if note_time + note_duration > bar_duration:
                        score.tracks[track_key][bar_idx]["duration"][note_idx] = bar_duration - note_time
        return score

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
                ) | (
                    np.all(
                        self.tracks[(idx, program, is_drum)][j]["velocity"]
                        <= self.MINIMUM_VELOCITY
                    )
                )
        return mask

    def get_silenced_bars(self):
        """ """
        silenced_mask = self.get_silenced_mask()
        silenced_bars = np.all(silenced_mask == 1, axis=0)
        return silenced_bars

    def cut_silenced_bars_at_beginning_and_end(self):
        """Cut silenced bars at the beginning and end of the score
        Cut the bar only if all tracks do not have notes (or fake notes)


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
        if np.sum(mask) == 0:
            raise ValueError("Mask must have at least one 1")

    def check_times(self):
        """ """
        for track_key in self.track_keys:
            idx, program, is_drum = track_key
            if len(self.tracks[(idx, program, is_drum)]) != len(
                self.bars
            ):
                raise ValueError("Track and bar length mismatch")


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

    @property
    def instruments(self):
        """
        Get the list of instruments in the score as a list of strings

        Returns
        -------
        instruments: list of str

        """
        from maidi.constants import REVERSE_INSTRUMENT_DICT
        return [REVERSE_INSTRUMENT_DICT[(track_key[1], track_key[2])] for track_key in self.track_keys]


    def dilate_time(self, factors):
        """
        Dilate the time of the notes in the score to match the time signature of the score

        Parameters
        ----------
        factor : float or list of float
            Factor to dilate the time of the notes, if a list is provided, the factors are applied to each bar
        """

        score = self.copy()
        for track_key in score.track_keys:
            for bar in range(len(score.bars)):
                factor = factors if isinstance(factors, (int, float)) else factors[bar]
                track = score.tracks[track_key][bar]
                track["time"] = (track["time"] * factor).astype(np.int32)
                track["duration"] = (track["duration"] * factor).astype(np.int32)
        return score

    def change_ts(self, new_ts, dilate_time=True):
        """
        Change the time signature of the score

        Parameters
        ----------

        new_ts : tuple
            New time signature of the score
        dilate_time : bool (Default value = True)
            If True, dilate the time of the notes to match the new time signature

        """

        score = self.copy()
        dilate_factors = []
        new_bars = []
        for idx_bar, bar in enumerate(score.bars):
            original_bar_duration = self._get_bar_duration_from_bar(bar, score.tpq)
            new_bar = list(bar)
            new_bar[self.TIME_SIGNATURE_NUMERATOR_INDEX] = new_ts[0]
            new_bar[self.TIME_SIGNATURE_DENOMINATOR_INDEX] = new_ts[1]
            new_bars.append(tuple(new_bar))
            new_bar_duration = self._get_bar_duration_from_bar(new_bar, score.tpq)
            dilate_factors.append(new_bar_duration / original_bar_duration)
        score.bars = new_bars
        if dilate_time:
            score = score.dilate_time(dilate_factors)
        return score

    @classmethod
    def from_empty(cls, instruments, nb_bars, ts=(4, 4), tempo=120, tpq=24, add_fake_notes=True):
        """

        Parameters
        ----------
        instruments :
            
        nb_bars : int
            Number of bars to create
            
             (Default value = (4)
        ts : tuple
            Time signature of the score (Default value = (4, 4))
        4) :
            
        tempo : int (Default value = 120)
            Tempo of the score

        tpq : int (Default value = 24)
            Ticks per quarter note, usually you don't need to change this

        add_fake_notes : bool (Default value = True)
            If True, add fake notes to the score (a ghost note with low velocity that is not considered in the generation)


        Returns
        -------

        """
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
            ]
            for _ in range(nb_bars)
        ]
        assert len(bars) == nb_bars, "Bars length mismatch"
        tracks = {}
        for track_key in track_keys:
            if add_fake_notes:
                tracks[track_key] = [cls._get_fake_note_vector() for _ in range(nb_bars)]
            else:
                tracks[track_key] = [cls._get_empty_note_vector() for _ in range(nb_bars)]

            assert len(tracks[track_key]) == nb_bars, "Track and bar length mismatch"

        return cls(bars, tracks, track_keys, tempo, tpq=tpq)
