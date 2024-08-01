from .chord_analyzer import parse_roman_numeral_notation
from maidi.analysis import Tags
from copy import deepcopy

ADDED_NOTE_TO_TAG = {

    '[addb9]': Tags.special_notes.diminished_ninth,
    '[add9]': Tags.special_notes.ninth,
    '[add#9]': Tags.special_notes.minor_third,
    '[add#10]': Tags.special_notes.major_third,
    '[add11]': Tags.special_notes.eleventh,
    '[addb5]': Tags.special_notes.diminished_fifth,
    '[add#11]': Tags.special_notes.diminished_fifth,
    '[add6]': Tags.special_notes.sixth,
    '[addb6]': Tags.special_notes.minor_sixth,
    '[add#6]': Tags.special_notes.major_sixth,
    '[addb13]': Tags.special_notes.minor_sixth,
    '[add13]': Tags.special_notes.sixth,
    '[add#13]': Tags.special_notes.major_sixth,
    '[addb7]': Tags.special_notes.minor_seventh,
    '[add7]': Tags.special_notes.major_seventh,
}

class ChordManager:

    tags = Tags

    def __init__(self, chords):
        if isinstance(chords, ChordManager):
            chords = chords.to_chords()

        self.chords = []
        for chord in chords:
            if chord is None:
                chord = self.get_none_chord()
            elif len(chord) == 4:
                chord = (*chord, [])
            self.chords.append(chord)

    def get_chord(self, bar):

        return self.chords[bar]

    def __getitem__(self, item):
        if isinstance(item, slice):
            return ChordManager(self.chords[item])
        else:
            chord = self.chords[item]
            return self.to_chord(chord)

    def __iter__(self):
        return iter(self.chords)

    @classmethod
    def to_chord(self, chord):
        return tuple(list(chord)[:4]) if chord[0] is not None else None

    @classmethod
    def get_none_chord(cls):
        return (None, None, None, [])

    def __setitem__(self, key, value):

            if isinstance(key, slice):
                if isinstance(value, (tuple, list)) and not isinstance(value[0], (tuple, list)):
                    value = [value for _ in range(*key.indices(len(self.chords)))]
                elif value is None:
                    value = [self.get_none_chord() for _ in self.chords[key]]
                elif isinstance(value, list):
                    indices = range(*key.indices(len(self.chords)))
                    expected_length = len(indices)
                    if len(value) != expected_length:
                        raise ValueError(f'Wrong number of chords assigned, expected {len(key.indices(len(self.chords)))}, got {len(value)}')
                    value = [self.get_none_chord() if chord is None else chord for chord in value]
                    for indice, val in zip(indices, value):
                        self[indice] = val

            elif isinstance(key, int):
                if value is None:
                    value = self.get_none_chord()
                elif isinstance(value, str):
                    value = parse_roman_numeral_notation(value)[0]

            print(value)
            self.chords[key] = value

    def __len__(self):
            return len(self.chords)

    def __repr__(self):
        return f'ChordManager({self.chords})'

    def to_chords(self):
        return deepcopy([self.to_chord(chord) for chord in self.chords])

    @classmethod
    def parse_added_notes_as_tags(cls, added_notes):
        tags = []
        for note in added_notes:
            tag = ADDED_NOTE_TO_TAG.get(note)
            if tag is not None:
                tags.append(tag)
        return tags

    @classmethod
    def from_roman_string(cls, roman_string):

        chords = parse_roman_numeral_notation(roman_string)
        chords = [(degree, tonality, mode, extension, cls.parse_added_notes_as_tags(added_notes)) for degree, tonality, mode, extension, added_notes in chords]

        return cls(chords)