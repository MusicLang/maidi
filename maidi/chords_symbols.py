I = 0
II = 1
III = 2
IV = 3
V = 4
VI = 5
VII = 6

C = 0
Db = 1
Cs = 1
D = 2
Eb = 3
Ds = 3
E = 4
Es = 5
Fb = 4
F = 5
Fs = 6
Gb = 6
G = 7
Gs = 8
Ab = 8
A = 9
As = 10
Bb = 10
B = 11
Bs = 0

minor = 'm'
major = 'M'

_root_position = ''
_triad = ''
_6 = '6'
_64 = '64'
_7 = '7'
_65 = '65'
_43 = '43'
_2 = '2'
_sus2 = '(sus2)'
_sus4 = '(sus4)'
ALL_EXTENSIONS = set([_root_position, _6, _64, _7, _65, _43, _2])
SPECIAL_EXTENSIONS = set([_sus4, _sus2])


def is_valid_extension(extension):
    corr_extension = extension.replace(_sus2, '').replace(_sus4, '')
    if extension in SPECIAL_EXTENSIONS:
        return True

    for ext in SPECIAL_EXTENSIONS:
        if extension.startswith(ext):
            return False

    return corr_extension in ALL_EXTENSIONS


