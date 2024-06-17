

class TagsCategory:
    ALL = []
    ranked = True

    @classmethod
    def higher(cls, tag):
        if not cls.ranked:
            raise Exception('This category is not ranked')
        index = cls.ALL.index(tag)
        if index == len(cls.ALL) - 1:
            return tag
        return cls.ALL[index + 1]

    @classmethod
    def lower(cls, tag):
        if not cls.ranked:
            raise Exception('This category is not ranked')

        index = cls.ALL.index(tag)
        if index == 0:
            return tag
        return cls.ALL[index - 1]

class Density(TagsCategory):

    lowest = 'CONTROL_DENSITY__LOWEST'
    lower = 'CONTROL_DENSITY__LOWER'
    low = 'CONTROL_DENSITY__LOW'
    medium_low = 'CONTROL_DENSITY__MEDIUM_LOW'
    medium = 'CONTROL_DENSITY__MEDIUM'
    high = 'CONTROL_DENSITY__HIGH'
    very_high = 'CONTROL_DENSITY__VERY_HIGH'

class MinRegister(TagsCategory):

    lowest = 'CONTROL_MIN_REGISTER__lowest'
    contrabass = 'CONTROL_MIN_REGISTER__contrabass'
    bass = 'CONTROL_MIN_REGISTER__bass'
    baritone = 'CONTROL_MIN_REGISTER__baritone'
    tenor = 'CONTROL_MIN_REGISTER__tenor'
    contralto = 'CONTROL_MIN_REGISTER__contralto'
    alto = 'CONTROL_MIN_REGISTER__alto'
    mezzo_soprano = 'CONTROL_MIN_REGISTER__mezzo_soprano'
    soprano = 'CONTROL_MIN_REGISTER__soprano'
    sopranissimo = 'CONTROL_MIN_REGISTER__sopranissimo'
    highest = 'CONTROL_MIN_REGISTER__highest'

    ALL = [lowest, contrabass, bass, baritone, tenor, contralto, alto, mezzo_soprano, soprano, sopranissimo, highest]


class MaxRegister(TagsCategory):
    lowest = 'CONTROL_MAX_REGISTER__lowest'
    contrabass = 'CONTROL_MAX_REGISTER__contrabass'
    bass = 'CONTROL_MAX_REGISTER__bass'
    baritone = 'CONTROL_MAX_REGISTER__baritone'
    tenor = 'CONTROL_MAX_REGISTER__tenor'
    contralto = 'CONTROL_MAX_REGISTER__contralto'
    alto = 'CONTROL_MAX_REGISTER__alto'
    mezzo_soprano = 'CONTROL_MAX_REGISTER__mezzo_soprano'
    soprano = 'CONTROL_MAX_REGISTER__soprano'
    sopranissimo = 'CONTROL_MAX_REGISTER__sopranissimo'
    highest = 'CONTROL_MAX_REGISTER__highest'
    ALL = [lowest, contrabass, bass, baritone, tenor, contralto, alto, mezzo_soprano, soprano, sopranissimo, highest]


class MinPolyphony(TagsCategory):

    zero = 'CONTROL_MIN_POLYPHONY__0'
    one = 'CONTROL_MIN_POLYPHONY__1'
    two = 'CONTROL_MIN_POLYPHONY__2'
    three = 'CONTROL_MIN_POLYPHONY__3'
    four = 'CONTROL_MIN_POLYPHONY__4'
    five = 'CONTROL_MIN_POLYPHONY__5'
    six = 'CONTROL_MIN_POLYPHONY__6'

    ALL = [zero, one, two, three, four, five, six]

class MaxPolyphony(TagsCategory):

        zero = 'CONTROL_MAX_POLYPHONY__0'
        one = 'CONTROL_MAX_POLYPHONY__1'
        two = 'CONTROL_MAX_POLYPHONY__2'
        three = 'CONTROL_MAX_POLYPHONY__3'
        four = 'CONTROL_MAX_POLYPHONY__4'
        five = 'CONTROL_MAX_POLYPHONY__5'
        six = 'CONTROL_MAX_POLYPHONY__6'

        ALL = [zero, one, two, three, four, five, six]


class SpecialNotes(TagsCategory):
    ranked = False

    eleventh = 'CONTROL_SPECIAL_NOTE__s3'
    ninth = 'CONTROL_SPECIAL_NOTE__s1'
    sixth = 'CONTROL_SPECIAL_NOTE__s5'
    diminished_ninth = 'CONTROL_SPECIAL_NOTE__h1'
    major_second = 'CONTROL_SPECIAL_NOTE__h2'
    minor_third = 'CONTROL_SPECIAL_NOTE__h3'
    major_third = 'CONTROL_SPECIAL_NOTE__h4'
    diminished_fifth = 'CONTROL_SPECIAL_NOTE__h6'
    minor_sixth = 'CONTROL_SPECIAL_NOTE__h8'
    major_sixth = 'CONTROL_SPECIAL_NOTE__h9'
    minor_seventh = 'CONTROL_SPECIAL_NOTE__h10'
    major_seventh = 'CONTROL_SPECIAL_NOTE__h11'

    ALL = [eleventh, ninth, sixth, diminished_ninth, major_second,
           minor_third, major_third, diminished_fifth, minor_sixth, major_sixth, minor_seventh, major_seventh]



class Tags:

    density = Density
    min_register = MinRegister
    max_register = MaxRegister
    min_polyphony = MinPolyphony
    max_polyphony = MaxPolyphony
    special_notes = SpecialNotes

    ALL = density.ALL + min_register.ALL + max_register.ALL + min_polyphony.ALL + max_polyphony.ALL + special_notes.ALL

    @staticmethod
    def get_tags_names():
        return Tags.ALL
