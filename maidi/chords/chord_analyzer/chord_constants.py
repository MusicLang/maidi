import re

DICT_TONALITY = {
    'M': {
        'I': (0, 'M'),
        'II': (2, 'M'),
        'III': (4, 'M'),
        'IV': (5, 'M'),
        'V': (7, 'M'),
        'VI': (9, 'M'),
        'VII': (11, 'M'),
        'i': (0, 'm'),
        'ii': (2, 'm'),
        'iii': (4, 'm'),
        'iv': (5, 'm'),
        'v': (7, 'm'),
        'vi': (9, 'm'),
        'vii': (11, 'm'),
        'bII': (1, 'M'),
        'bii': (1, 'm'),
        'bIII': (3, 'M'),
        'biii': (3, 'm'),
        'bV': (6, 'M'),
        'bv': (6, 'm'),
        'bVI': (8, 'M'),
        '#VI': (9, 'M'),
        '#vi': (9, 'm'),
        'bvi': (8, 'M'),
        'bVII': (10, 'M'),
        'bvii': (10, 'm'),
        '#IV': (6, 'M'),
        '#iv': (6, 'm'),
        '#VII': (11, 'M'),
        '#vii': (11, 'm'),
        'Ger': (1, 'M'),
        'It': (1, 'M'),
        'Fr': (1, 'M'),
        'N': (1, 'M'),
        '#i': (1, 'm'),
        '#I': (1, 'M'),
        '#ii': (3, 'm'),
        '#II': (3, 'M'),
        'bbii': (0, 'm'),
        'bbII': (0, 'M'),
        "bbIII": (2, "M"),
        "bbiii": (2, "m"),
        'bbvi': (7, 'm'),
        'bbVI': (7, 'M'),
        'bbvii': (9, 'm'),
        'bbVII': (9, 'M'),
        '#V': (8, 'M'),
        '#v': (8, 'm'),
        'biv': (4, 'm'),
        "bbiv": (3, "m"),
        "bbIV": (3, "M"),
        'bbv': (5, 'm'),
        'bbV': (5, 'M'),
        'bbI': (10, 'M'),
        'bI': (11, 'M'),
        'bi': (11, 'm'),
        "bbi": (10, "m"),
        "#III": (5, "M"),
        "#iii": (5, "m"),
    },
    'm': {
        'I': (0, 'M'),
        'II': (2, 'M'),
        'III': (3, 'M'),
        '#III': (4, 'M'),
        'bIV': (4, 'M'),
        'IV': (5, 'M'),
        'V': (7, 'M'),
        'VI': (8, 'M'),
        'VII': (10, 'M'),
        'i': (0, 'm'),
        'ii': (2, 'm'),
        'iii': (3, 'm'),
        'iv': (5, 'm'),
        'v': (7, 'm'),
        'vi': (9, 'm'),
        'vii': (11, 'm'),
        'bII': (1, 'M'),
        'bii': (1, 'm'),
        'bIII': (3, 'M'),
        'biii': (3, 'm'),
        'bV': (6, 'M'),
        'bv': (6, 'm'),
        'bVI': (8, 'M'),
        'bvi': (8, 'M'),
        '#VI': (9, 'M'),
        '#vi': (9, 'm'),
        'bVII': (10, 'M'),
        'bvii': (10, 'm'),
        'bbvii': (9, 'm'),
        'bbVII': (9, 'M'),
        '#VII': (11, 'M'),
        '#vii': (11, 'm'),
        '#IV': (6, 'M'),
        '#iv': (6, 'm'),
        'Ger': (1, 'M'),
        'It': (1, 'M'),
        'Fr': (1, 'M'),
        'N': (1, 'M'),
        '#i': (1, 'm'),
        '#I': (1, 'M'),
        '#ii': (3, 'm'),
        '#II': (3, 'M'),
        'bbii': (0, 'm'),
        'bbII': (0, 'M'),
        "bbIII": (1, "M"),
        "bbiii": (1, "m"),
        'bbvi': (7, 'm'),
        'bbVI': (6, 'M'),
        '#V': (8, 'M'),
        '#v': (8, 'm'),
        'biv': (4, 'm'),
        "bbiv": (3, "m"),
        "bbIV": (3, "M"),
        'bbv': (5, 'm'),
        'bbV': (5, 'M'),
        'bI': (11, 'M'),
        'bi': (11, 'm'),
        "bbi": (10, "m"),
        "bbI": (10, "M"),
        "#iii": (4, "m"),
    }
}

DICT_TONALITY_REVERSE = {
    'M': {value: key for key, value in reversed(DICT_TONALITY['M'].items())},
    'm': {value: key for key, value in reversed(DICT_TONALITY['m'].items())}
}

DICT_RELATIVE_CHANGE = {
    'M': {
        'I': (0, 'M', 0),  # Degree, mode, offset tonality
        'II': (4, 'M', 7),
        'III': (4, 'm', 9),
        'IV': (3, 'M', 0),
        'V': (4, 'M', 0),
        'VI': (4, 'm', 2),
        'VII': (4, 'm', 4),
        'i': (0, 'm', 0),
        'ii': (1, 'M', 0),
        'iii': (2, 'M', 0),
        'iv': (3, 'm', 0),
        'v': (0, 'm', 7),
        'vi': (5, 'M', 0),
        'vii': (5, 'M', 2),
        'bII': (4, 'M', 6),
        'bii': (0, 'm', 1),
        'bIII': (0, 'M', 3),
        'biii': (0, 'm', 3),
        'bV': (0, 'M', 6),
        'bv': (0, 'm', 6),
        'bVI': (0, 'M', 8),
        'bvi': (0, 'm', 8),
        'bVII': (0, 'M', 10),
        'bvii': (0, 'm', 10),
        '#IV': (0, 'M', 6),
        '#iv': (0, 'm', 6),
        '#VII': (0, 'M', 11),
        '#vii': (0, 'm', 11),
        'Ger': (4, 'M', 1),
        'It': (4, 'M', 1),
        'Fr': (4, 'M', 1),
        'N': (4, 'm', 6),
        'io': (6, 'm', 1),
        'iø': (6, 'M', 1),
        'iio': (6, 'm', 3),
        'iiø': (1, 'm', 0),
        'iiio': (6, 'm', 5),
        'iiiø': (6, 'M', 5),
        'ivo': (6, 'm', 6),
        'ivø': (6, 'M', 6),
        'vo': (6, 'm', 8),
        'vø': (6, 'M', 8),
        'vio': (6, 'm', 10),
        'viø': (6, 'M', 10),
        '#vio': (6, 'm', 10),
        '#viø': (6, 'M', 10),
        'viio': (6, 'm', 0),
        'viiø': (6, 'M', 0),
        'Cad': (0, 'M', 0),
        '#ivo': (6, 'm', 7),
        '#ivø': (6, 'M', 7),
        "#iiio": (6, 'm', 5),
        '#viio': (6, 'm', 0),
        #"III+": (2, 'm', 1)
    },
    'm': {
        'I': (0, 'M', 0),  # Degree, mode, offset tonality
        'II': (4, 'M', 7),
        'III': (0, 'M', 3),
        'IV': (3, 'M', 0),
        'V': (4, 'm', 0),
        'VI': (3, 'M', 3),
        'VII': (4, 'M', 3),
        'i': (0, 'm', 0),
        'ii': (1, 'M', 0),
        'iii': (2, 'M', 0),
        '#iii': (0, 'm', 4),
        'iv': (3, 'm', 0),
        'v': (0, 'm', 7),
        'vi': (5, 'M', 0),
        'vii': (5, 'M', 2),
        'bII': (4, 'M', 6),
        'bii': (0, 'm', 1),
        'bIII': (0, 'M', 3),
        'biii': (0, 'm', 3),
        'bV': (0, 'M', 6),
        'bv': (0, 'm', 6),
        'bVI': (0, 'M', 8),
        'bvi': (0, 'm', 8),
        'bVII': (4, 'M', 3),
        'bvii': (0, 'm', 10),
        '#IV': (0, 'M', 6),
        '#iv': (0, 'm', 6),
        '#VII': (0, 'M', 11),
        '#vii': (0, 'm', 11),
        'Ger': (4, 'M', 1),
        'It': (4, 'M', 1),
        'Fr': (4, 'M', 1),
        'N': (4, 'm', 6),
        'io': (6, 'm', 1),
        'iø': (6, 'M', 1),
        'iio': (6, 'm', 3),
        'iiø': (1, 'm', 0),
        'iiio': (6, 'm', 5),
        'iiiø': (6, 'M', 5),
        'ivo': (6, 'm', 6),
        'ivø': (6, 'M', 6),
        'vo': (6, 'm', 8),
        'vø': (6, 'M', 8),
        'vio': (6, 'm', 10),
        'viø': (6, 'M', 10),
        '#vio': (6, 'm', 10),
        '#viø': (6, 'M', 10),
        'viio': (6, 'm', 0),
        'viiø': (6, 'M', 0),
        'Cad': (0, 'm', 0),
        '#ivo': (6, 'm', 7),
        '#ivø': (6, 'M', 7),
        "#iiio": (6, 'm', 5),
        'III+': (2, 'm', 0),
        '#viio': (6, 'm', 0),
    }
}

EXTENSION_REPLACER = (
    ('M7', '(M7)'),
    ('maj7', '(M7)'),
    ('m7', '(m7)'),
    ('min7', '(m7)'),
    ('+', '(+)'),
    ('b3', '(M2)'),
    ('b5', '(b5)'),
    ('b7', '(m7)'),
    ('b9', '(m9)'),
    ('ar', ''),
    ('add2', '[add2]'),
    ('addb2', '[m2]'),
    ('addb3', '[m3]'),
    ('addb5', '[b5]'),
    ('addb6', '[m6]'),
    ('addb7', '[m7]'),
    ('addb9', '[m9]'),
    ('add#2', '[m3]'),
    ('add#4', '[#11]'),
    ('add4', '[add4]'),
    ('add6', '[add6]'),
    ('add#6', '[M6]'),
    ('add7', '[add7]'),
    ('add#7', '[M7]'),
    ('add9', '[add9]'),
    ('add#9', '[M9]'),
    ('add11', '[add11]'),
    ('add#11', '[#11]'),
    ('add13', '[add13]'),
    ('add#13', '[M13]'),
    ('sus2', '(sus2)'),
    ('sus4', '(sus4)'),
    ('no5', '{-5}'),
    ('no3', '{-3}'),
    ('no1', '{-1}'),
    ('no7', '{-7}'),
    ('no9', '{-9}'),
    ('no11', '{-11}'),
    ('no8', '{-1}'),
)

DEGREE_REGEX = re.compile(r'(Cad|III\+|N|Ger|Fr|It|[b|#]*?[I|V|i|v|o|ø]+)')
