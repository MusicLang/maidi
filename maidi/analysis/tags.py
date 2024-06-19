class Tag:

    def __init__(self, root: str, value: str):
        self.root = root
        self.value = value

    def to_tag(self):
        return f"{self.root}__{self.value}"


class TagsProvider:
    ALL_TAGS = None

    def get_tags_list(self):
        if self.ALL_TAGS is None:
            raise ValueError("ALL_TAGS is not defined for the provider class, it should be a list of all tags")

        return self.ALL_TAGS

    def get_tags(self, track_bar, bar, score):
        raise NotImplementedError


    def get_pitches(self, track_bar, bar, score):
        pitches = track_bar["pitch"]
        return list(pitches)

    def get_start_end_notes(self, track_bar, bar, score):
        from maidi.utils.bar_helpers import bar_to_bar_duration_in_quarters
        times = track_bar["time"]
        durations = track_bar["duration"]
        ends = times + durations
        notes = list(zip(times, ends))
        return notes

class ScoreTagger:

    def __init__(self, tags_providers):
        self.tags_providers = tags_providers

    def remove_fake_notes(self, track_bar):
        """
        Remove notes that have velocity < 2

        """
        from maidi import MidiScore
        index = track_bar["velocity"] >= MidiScore.MINIMUM_VELOCITY
        new_track_bar = {}
        for key in track_bar.keys():
            new_track_bar[key] = track_bar[key][index]
        return new_track_bar


    @classmethod
    def get_base_tagger(cls):
        from maidi.analysis import tags_providers
        return ScoreTagger(
            [
                tags_providers.DensityTagsProvider(),
                tags_providers.MinMaxRegisterTagsProvider(),
                tags_providers.SpecialNotesTagsProvider(),
                tags_providers.MinMaxPolyphonyTagsProvider(),
            ]
        )

    def tag_score(self, score):
        tags = []

        for idx_track, track_key in enumerate(score.track_keys):
            track_tags = []
            for idx_bar in range(score.nb_bars):
                bar_tags = []
                track_bar = score.get_track_bar(idx_track, idx_bar)
                bar = score.bars[idx_bar]
                for provider in self.tags_providers:
                    track_bar = self.remove_fake_notes(track_bar)
                    bar_tags += provider.get_tags(track_bar, bar, score)
                track_tags.append(bar_tags)
            tags.append(track_tags)

        from maidi import TagManager
        return TagManager(tags)
