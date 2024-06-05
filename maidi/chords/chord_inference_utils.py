import numpy as np
import os
import pickle

TEMPLATES = [
    ("", [0, 4, 7], 1),
    ("(m3)", [0, 3, 7], 1),
    ("(m3)(b5)", [0, 3, 6], 1.0),
    ("(m3)(b5)[add6]", [0, 3, 6, 9], 1.0),
    ("(+)", [0, 4, 8], 0.8),
    ("(sus2)", [0, 2, 7], 0.85),
    ("(sus4)", [0, 5, 7], 0.85),
    ("(M7)", [0, 4, 7, 11], 0.7),
    ("(m3)(m7)", [0, 3, 7, 10], 0.9),
    ("(m3)(M7)", [0, 3, 7, 10], 0.8),
    ("(m7)", [0, 4, 7, 10], 1.0),
    ("(m3)(m7)(b5)", [0, 3, 6, 10], 0.95),
]

EXTENSIONS = [
    "",
    "7",
    "(+)",
    "(sus2)",
    "(sus4)",
]
CHORD_TYPE_TO_PITCHES = {t[0]: t[1] for t in TEMPLATES}
CHORD_TYPES = np.asarray([t[0] for t in TEMPLATES])
PITCH_CLASS = np.arange(12)

CHROMA_VECTORS = [t[1] for t in TEMPLATES]
COEFFS = np.asarray([t[2] for t in TEMPLATES])
# Convert chroma_vectors into a 12xn_chords matrix with each row being the indexes of the chroma_vector
CHROMA_VECTORS_MATRIX = np.asarray(
    [
        [(1.0 * (i % 12)) in chroma_vector for i in range(12)]
        for chroma_vector in CHROMA_VECTORS
    ]
)
CHROMA_VECTORS_MATRIX = np.concatenate(
    [np.roll(CHROMA_VECTORS_MATRIX, i, axis=1) for i in range(12)], axis=0
)
COEFFS = np.concatenate([COEFFS for i in range(12)], axis=0)

MODES = ["M", "m"]
TONALITIES = list(range(12))
ROMAN_NUMERALS = list(range(7))

SCALES = {"M": [0, 2, 4, 5, 7, 9, 11], "m": [0, 2, 3, 5, 7, 8, 11]}


this_file_path = os.path.dirname(os.path.realpath(__file__))
pitch_class_dict_path = os.path.join(this_file_path, "../metadata/pitch_classes_dict.pkl")
pitches_dict_path = os.path.join(this_file_path, "../metadata/pitches_dict.pkl")
pitches_dict_roots_path = os.path.join(
    this_file_path, "../metadata/pitches_dict_roots.pkl"
)
with open(pitch_class_dict_path, "rb") as f:
    PITCH_CLASSES_DICT = pickle.load(f)

with open(pitches_dict_path, "rb") as f:
    PITCHES_DICT = pickle.load(f)

with open(pitches_dict_roots_path, "rb") as f:
    PITCHES_DICT_ROOT = pickle.load(f)
