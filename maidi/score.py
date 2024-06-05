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
    """ """

    SCALE_DEGREE_INDEX = 0
    TONALITY_INDEX = 1
    MODE_INDEX = 2
    CHORD_OCTAVE_INDEX = 3
    CHORD_EXTENSION_INDEX = 4
    TIME_SIGNATURE_NUMERATOR_INDEX = 5
    TIME_SIGNATURE_DENOMINATOR_INDEX = 6
    TIME_TICK_START_INDEX = 7
    TIME_TICK_END_INDEX = 8
    FAKE_NOTE_VELOCITY = 1  # Should be < 2 to be ignored by the model
    FAKE_NOTE_DURATION = 2
    FAKE_NOTE_PITCH = 60

    def __init__(self, chords, tracks, track_keys, tempo, tpq=24, **kwargs):
        self.chords = chords
        self.tracks = tracks
        self.track_keys = track_keys
        self.tempo = tempo
        self.tpq = tpq
        self.kwargs = kwargs

    @classmethod
    def from_midi(cls, midi_file, tpq=24, chord_range=None):
        """

        Parameters
        ----------
        midi_file :
            
        tpq :
             (Default value = 24)
        chord_range :
             (Default value = None)

        Returns
        -------

        """
        from maidi.parser import Parser

        parser = Parser(tpq=tpq)
        chords, tracks, track_keys, tempo = parser.parse(midi_file)
        score = cls(chords, tracks, track_keys, tempo, tpq=tpq)
        if chord_range is not None:
            score = score.get_score_between(*chord_range)
        return score

    @property
    def shape(self):
        """ """
        return len(self.track_keys), len(self.chords)
    @property
    def nb_tracks(self):
        """ """
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
        score = self
        if isinstance(item, tuple):
            first_dim, second_dim = item
            subtrack_score = score.get_tracks(first_dim)
            return subtrack_score.get_bars(second_dim)

        if isinstance(item, (slice, int)):
            return score.get_tracks(item)

    def __setitem__(self, item, value):
        if not isinstance(value, MidiScore):
            raise TypeError("Value must be a MidiScore instance")

        if isinstance(item, int):
            # Single integer index implies updating a specific track across all tracks
            track_indexes = [item]

            # Ensure the value has the same structure
            if len(value.shape[0]) != 1:
                raise ValueError("The provided MidiScore must have one track")
            if len(value.shape[1]) != len(self.chords):
                raise ValueError("The provided MidiScore must have the same number of bars")

            # Update the track notes
            self.assign_tracks(track_indexes, value)

        elif isinstance(item, slice):
            start, end = item.start, item.stop
            if start is None and end is None:
                return value
            start = start if start is not None else 0
            end = end if end is not None else len(self.track_keys)
            track_indexes = range(start, end)
            self.assign_tracks(track_indexes, value)

        if isinstance(item, tuple):

            first_dim, second_dim = item
            if isinstance(first_dim, int):
                first_dim = slice(first_dim, first_dim + 1)
            if isinstance(second_dim, int):
                second_dim = slice(second_dim, second_dim + 1)

            start_first_dim = first_dim.start if first_dim.start is not None else 0
            end_first_dim = first_dim.stop if first_dim.stop is not None else len(self.track_keys)
            start_second_dim = second_dim.start if second_dim.start is not None else 0
            end_second_dim = second_dim.stop if second_dim.stop is not None else len(self.chords)

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
                for bar_idx in range(len(self.chords)):
                    self.tracks[self_track][bar_idx] = other_score.tracks[value_track][bar_idx]
            else:
                for abs_idx, bar_idx in enumerate(range(*bar_range)):
                    self.tracks[self_track][bar_idx] = other_score.tracks[value_track][abs_idx]

    def get_track_from_index(self, index):
        return self.tracks[self.track_keys[index]]

    def get_track_bar(self, idx_track, idx_bar):
        return self.tracks[self.track_keys[idx_track]][idx_bar]

    def get_chords_prompt(self):
        kept_indexes = [self.SCALE_DEGREE_INDEX, self.TONALITY_INDEX, self.MODE_INDEX, self.CHORD_EXTENSION_INDEX]
        return [[chord[index] for index in kept_indexes] for chord in self.chords]
    def get_bars(self, item):
        """
        Get the bars between the start and end index

        slice: int or Slice, slice object
        """
        if isinstance(item, int):
            item = slice(item, item + 1)
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
            item = slice(item, item + 1)
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
        self = self.copy()
        new_chords = deepcopy(self.chords)
        new_tracks = deepcopy(self.tracks)
        removed_chord = new_chords.pop(bar_index)
        removed_chord_duration = (
            removed_chord[self.TIME_TICK_END_INDEX]
            - removed_chord[self.TIME_TICK_START_INDEX]
        )
        # Offset the start and end time of the chords
        for i in range(bar_index, len(new_chords)):
            new_chords[i][self.TIME_TICK_START_INDEX] -= removed_chord_duration
            new_chords[i][self.TIME_TICK_END_INDEX] -= removed_chord_duration

        for track_key in self.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)].pop(bar_index)

        return MidiScore(new_chords, new_tracks, self.track_keys, self.tempo, self.tpq)

    @classmethod
    def get_fake_note_vector(cls):
        """ """
        return {
            "time": np.asarray([0], dtype=np.int32),
            "pitch": np.asarray([cls.FAKE_NOTE_PITCH], dtype=np.int8),
            "duration": np.asarray([cls.FAKE_NOTE_DURATION], dtype=np.int32),
            "velocity": np.asarray([cls.FAKE_NOTE_VELOCITY], dtype=np.int8),
        }

    def add_bar(self, bar_index):
        """

        Parameters
        ----------
        bar_index :
            

        Returns
        -------

        """
        score = self.copy()
        new_chords = deepcopy(score.chords)
        new_tracks = deepcopy(score.tracks)
        new_chords.insert(bar_index + 1, deepcopy(new_chords[bar_index]))
        chord_duration = (
            new_chords[bar_index][score.TIME_TICK_END_INDEX]
            - new_chords[bar_index][score.TIME_TICK_START_INDEX]
        )
        # Offset the start and end time of the chords
        for i in range(bar_index + 1, len(new_chords)):
            new_chords[i][score.TIME_TICK_START_INDEX] += chord_duration
            new_chords[i][score.TIME_TICK_END_INDEX] += chord_duration

        for track_key in score.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)].insert(
                bar_index + 1, score.get_fake_note_vector()
            )

        return MidiScore(new_chords, new_tracks, score.track_keys, score.tempo, score.tpq)

    def notes_to_note_tick_list(self, notes, chords):
        """

        Parameters
        ----------
        notes :
            
        chords :
            

        Returns
        -------

        """
        note_tick_list = []
        for idx, (chord, note_list) in enumerate(zip(chords, notes)):
            for note in note_list:

                note_tick_list.append(
                    (
                        note.start,
                        note.end,
                        note.pitch,
                        chord[self.TIME_SIGNATURE_NUMERATOR_INDEX],
                        chord[self.TIME_SIGNATURE_DENOMINATOR_INDEX],
                        chord[self.TIME_TICK_START_INDEX],
                        chord[self.TIME_TICK_END_INDEX],
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
        for chord in self.chords:
            ts = TimeSignature(
                chord[self.TIME_TICK_START_INDEX],
                chord[self.TIME_SIGNATURE_NUMERATOR_INDEX],
                chord[self.TIME_SIGNATURE_DENOMINATOR_INDEX],
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
                self.chords, self.tracks[(idx, program, is_drum)]
            )
            score.tracks.append(track)

        score.dump_midi(filename)
        return score

    @classmethod
    def track_notes_to_score_notes(cls, chords, track_notes):
        """

        Parameters
        ----------
        chords :
            
        track_notes :
            

        Returns
        -------

        """
        notes = []
        has_note = False
        for idx_bar, chord_track_notes in enumerate(track_notes):
            for idx in range(len(chord_track_notes["time"])):
                time = (
                    chord_track_notes["time"][idx]
                    + chords[idx_bar][MidiScore.TIME_TICK_START_INDEX]
                )
                pitch = chord_track_notes["pitch"][idx]
                duration = chord_track_notes["duration"][idx]
                velocity = chord_track_notes["velocity"][idx]
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
        new_chords = deepcopy(self.chords)
        for chord in new_chords:
            chord[self.TIME_TICK_START_INDEX] += offset
            chord[self.TIME_TICK_END_INDEX] += offset
        return MidiScore(
            new_chords,
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

        new_chords = deepcopy(self.chords[start_bar:end_bar])
        if start_bar is None:
            start_bar = 0

        # If start bar > 0 we need to adjust the bar start and end time
        start_bar_tick = self.chords[start_bar][self.TIME_TICK_START_INDEX]
        if start_bar > 0:
            for chord in new_chords:
                chord[self.TIME_TICK_START_INDEX] -= start_bar_tick
                chord[self.TIME_TICK_END_INDEX] -= start_bar_tick
        assert all(
            [chord[self.TIME_TICK_START_INDEX] >= 0 for chord in new_chords]
        ), f"Negative time found in chords {new_chords}"
        new_tracks = {}
        for track_key in self.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)] = self.tracks[
                (idx, program, is_drum)
            ][start_bar:end_bar]
            assert len(new_tracks[(idx, program, is_drum)]) == len(
                new_chords
            ), "Track and chord length mismatch"
        return MidiScore(new_chords, new_tracks, self.track_keys, self.tempo, self.tpq)

    def copy(self):
        """ """
        return MidiScore(
            deepcopy(self.chords),
            deepcopy(self.tracks),
            deepcopy(self.track_keys),
            self.tempo,
            self.tpq,
        )

    def get_mask(self):
        """Get the mask of the score (np.array of shape (n_tracks, n_chords))
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        import numpy as np

        mask = np.zeros((len(self.track_keys), len(self.chords)))

        return mask

    def get_empty_controls(self, prevent_silence=False):
        """Get the mask, the tags and the chords of the current score.
        The mask is a np.array of shape (n_tracks, n_chords)
        The tags is a list of list of list of size (n_tracks, n_chords, <variable size>)
        The chords is a list of size (n_chords,)

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
        return len(self.chords)

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
        mask = np.zeros((len(self.track_keys), len(self.chords)))
        for i, track_key in enumerate(self.track_keys):
            idx, program, is_drum = track_key
            for j, chord in enumerate(self.chords):
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
            bar_to_cut_start, len(score.chords) - bar_to_cut_end
        )
        return score

    def check_mask(self, mask):
        """Check that the mask is valid

        Parameters
        ----------
        mask :
            np.array of shape (n_tracks, n_chords)

        Returns
        -------

        """
        if mask.shape[1] != len(self.chords):
            raise ValueError(
                f"Mask length does not match score length {mask.shape[1]} != {len(self.chords)}"
            )
        if mask.shape[1] > 16:
            raise ValueError("Mask length must be less than 16")
        if mask.shape[0] != len(self.track_keys):
            raise ValueError(
                "Mask number of tracks does not match score number of tracks"
            )

    def _create_temp_midi_files(self):
        """ """
        prompt_file = tempfile.NamedTemporaryFile(suffix=".txt").name
        output_file = tempfile.NamedTemporaryFile(suffix=".txt").name
        midi_file = tempfile.NamedTemporaryFile(suffix=".mid").name
        output_midi_file = tempfile.NamedTemporaryFile(suffix=".mid").name
        self.write(midi_file)
        return prompt_file, output_file, midi_file, output_midi_file

    def remove_temp_midi_files(
        self, prompt_file, output_file, midi_file, output_midi_file
    ):
        """

        Parameters
        ----------
        prompt_file :
            
        output_file :
            
        midi_file :
            
        output_midi_file :
            

        Returns
        -------

        """
        os.remove(prompt_file)
        os.remove(output_file)
        os.remove(midi_file)
        os.remove(output_midi_file)



    def check_times(self):
        """ """
        for track_key in self.track_keys:
            idx, program, is_drum = track_key
            assert len(self.tracks[(idx, program, is_drum)]) == len(
                self.chords
            ), "Track and chord length mismatch"

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
            for idx_chord, chord in enumerate(self.chords):
                chord_start = chord[self.TIME_TICK_START_INDEX]
                chord_end = chord[self.TIME_TICK_END_INDEX]
                chord_duration = chord_end - chord_start
                for idx_note, note in enumerate(
                    new_tracks[(idx, program, is_drum)][idx_chord]["time"]
                ):
                    if (
                        note
                        + new_tracks[(idx, program, is_drum)][idx_chord][
                            "duration"
                        ][idx_note]
                        > chord_duration
                    ):
                        new_tracks[(idx, program, is_drum)][idx_chord][
                            "duration"
                        ][idx_note] = (chord_duration - note)

        return MidiScore(
            deepcopy(self.chords),
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
        new_track_key = (len(self.track_keys), program, bool(is_drum))
        self.track_keys.append(new_track_key)
        self.tracks[new_track_key] = [
            self.get_fake_note_vector() for _ in range(len(self.chords))
        ]
        return self

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
            initial_length = len(score.chords)
            score = score.add_silence_bars(silence_bars, add_fake_notes=False)
            assert (
                len(score.chords) == initial_length + silence_bars
            ), "Silence bars not added correctly"
        other_score = other_score.copy()
        # Assert that the other score has the same tracks
        if other_score.track_keys != score.track_keys:
            if try_matching_tracks:
                score, other_score = self.match_track_keys(score, other_score)
            else:
                raise ValueError("Track keys do not match")
        # Offset the other score to start after the current score
        offset = score.chords[-1][score.TIME_TICK_END_INDEX]
        new_other_score = other_score.offset_score(offset)
        new_chords = score.chords + new_other_score.chords
        new_tracks = {}
        for track_key in score.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)] = (
                score.tracks[(idx, program, is_drum)]
                + new_other_score.tracks[(idx, program, is_drum)]
            )
        return MidiScore(
            new_chords, new_tracks, score.track_keys, score.tempo, score.tpq
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
        offset = score.chords[-1][score.TIME_TICK_END_INDEX]
        if n_bars <= 0:
            raise ValueError(
                "n_bars must be positive"
            )  # If we want to add silence bars
        offset += n_bars * (
            score.chords[-1][score.TIME_TICK_END_INDEX]
            - score.chords[-1][score.TIME_TICK_START_INDEX]
        )
        new_chords = score.chords
        time = new_chords[-1][score.TIME_TICK_END_INDEX]
        last_bar_duration = (
            score.chords[-1][score.TIME_TICK_END_INDEX]
            - score.chords[-1][score.TIME_TICK_START_INDEX]
        )
        for i in range(n_bars):
            new_chords.append(deepcopy(score.chords[-1]))
            new_chords[-1][score.TIME_TICK_START_INDEX] = time
            new_chords[-1][score.TIME_TICK_END_INDEX] = time + last_bar_duration
            time += last_bar_duration

        new_tracks = {}
        for track_key in score.track_keys:
            idx, program, is_drum = track_key
            new_tracks[(idx, program, is_drum)] = score.tracks[
                (idx, program, is_drum)
            ]
            for new_chord in new_chords[-n_bars:]:
                if add_fake_notes:
                    new_tracks[(idx, program, is_drum)].append(
                        self.get_fake_note_vector()
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
                new_chords
            ), "Track and chord length mismatch"
        return MidiScore(
            new_chords, new_tracks, score.track_keys, score.tempo, score.tpq
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
        chords = [
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
        assert len(chords) == nb_bars, "Chords length mismatch"
        tracks = {}
        for track_key in track_keys:
            tracks[track_key] = [cls.get_fake_note_vector() for _ in range(nb_bars)]

            assert len(tracks[track_key]) == nb_bars, "Track and chord length mismatch"

        return cls(chords, tracks, track_keys, tempo, tpq=tpq)
