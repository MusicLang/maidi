
from copy import deepcopy


class TagManager:

    def __init__(self, tags):
        """
        Create a tag manager

        Parameters
        ----------
        tags : list[list[list[str]]]
            The tags
        """
        if isinstance(tags, TagManager):
            self.tags = deepcopy(tags.tags)
        else:
            self.tags = deepcopy(tags)

    def add_to_tag(self, tag_category, value):
        return tag_category.add_value(self, value)

    def replace_all_with_tag(self, tag_category, new_tag):
        return tag_category.replace_all_with_tag(self, new_tag)

    def replace_tag(self, tag_to_change, new_tag):
        from maidi import TagManager
        from copy import deepcopy
        new_array = deepcopy(self.tags)
        for idx_track, track in enumerate(new_array):
            for idx_bar, bar in enumerate(track):
                for idx_value, tag in enumerate(bar):
                    if tag == tag_to_change:
                        new_array[idx_track][idx_bar][idx_value] = new_tag

        return TagManager(new_array)


    @classmethod
    def empty_from_score(cls, score):
        """
        Create an empty tag manager from a score

        Parameters
        ----------
        score : MidiScore
            The score to create the tag manager from

        Returns
        -------
        tag_manager : TagManager
            The tag manager
        """
        shape = score.shape
        tags = [[[] for _ in range(shape[1])] for _ in range(shape[0])]
        return cls(tags)

    @classmethod
    def from_chord_manager(cls, chord_manager, nb_tracks):
        """
        Create a tag manager from a score and a chord manager

        Parameters
        ----------
        chord_manager : ChordManager
            The chord manager in which to extract tags associated to chord progression
        nb_tracks : int
            The number of tracks
        """
        tags = [[[] for _ in range(len(chord_manager))] for _ in range(nb_tracks)]
        for idx_track in range(nb_tracks):
            for idx_bar in range(len(chord_manager)):
                tags[idx_track][idx_bar] = chord_manager.chords[idx_bar][4]
        return cls(tags)



    def add_tag(self, tag):
        """
        Add a tag

        Parameters
        ----------
        tag : str
            The tag to add

        Returns
        -------
        None
        """
        return self.add_tags([tag])


    def __repr__(self):
        repr = ""
        for idx_track, track in enumerate(self.tags):
            repr += f"Track {idx_track} \n"
            for bar_idx, bar in enumerate(track):
                repr += f" Bar {bar_idx} : " + str(bar) + "\n"
            repr += "\n"
        return repr


    def add_tags(self, tags):
        """
        Add tags

        Parameters
        ----------
        tags : list[str]
            The tags to add

        Returns
        -------
        None
        """
        for track in self.tags:
            for bar in track:
                bar.extend(tags)

    def add_tag_at_index(self, tag, track_index, bar_index):
        """
        Add a tag at a specific index

        Parameters
        ----------
        tag : str
            The tag to add
        track_index : int
            The track index
        bar_index : int
            The bar index

        Returns
        -------
        None
        """
        self.add_tags_at_index([tag], track_index, bar_index)

    def add_tags_at_index(self, tags, track_index, bar_index):
        """
        Add tags at a specific index

        Parameters
        ----------
        tags : list[str]
            The tags to add
        track_index : int
            The track index
        bar_index : int
            The bar index

        Returns
        -------
        None
        """
        self.tags[track_index][bar_index].extend(tags)


    def add_tag_for_track(self, tag, track_index):
        """
        Add a tag for a specific track

        Parameters
        ----------
        tag : str
            The tag to add
        track_index : int
            The track index
        """
        return self.add_tags_for_track([tag], track_index)


    def add_tags_for_track(self, tags, track_index):
        """
        Add tags for a specific track

        Parameters
        ----------
        tags : list[str]
            The tags to add
        track_index : int
        """
        for bar in self.tags[track_index]:
            bar.extend(tags)

    def add_tags_for_bar(self, tags, bar_index):
        """
        Add tags for a specific bar

        Parameters
        ----------
        tags : list[str]
            The tags to add
        bar_index : int
        """
        for track in self.tags:
            track[bar_index].extend(tags)

    def add_tag_for_bar(self, tag, bar_index):
        """
        Add a tag for a specific bar

        Parameters
        ----------
        tag : str
            The tag to add
        bar_index : int
        """
        return self.add_tags_for_bar([tag], bar_index)

    def remove_tags(self, tags):
        """
        Remove tags in the whole score

        Parameters
        ----------
        tags : list[str]
            The tags to remove

        """
        for track in self.tags:
            for bar in track:
                for tag in tags:
                    if tag in bar:
                        bar.remove(tag)

    def remove_tag(self, tag):
        """
        Remove a tag in the whole score

        Parameters
        ----------
        tag : str
            The tag to remove


        """
        for track in self.tags:
            for bar in track:
                if tag in bar:
                    bar.remove(tag)

    def remove_tag_for_track(self, tag, track_index):
        """
        Remove a tag for a specific track

        Parameters
        ----------
        tag : str
            The tag to remove
        track_index : int
            The track index

        """
        for bar in self.tags[track_index]:
            if tag in bar:
                bar.remove(tag)

    def remove_tags_for_track(self, tags, track_index):
        """
        Remove tags for a specific track

        Parameters
        ----------
        tags : list[str]
            The tags to remove
        track_index : int
            The track index

        """
        for idx, bar in enumerate(self.tags[track_index]):
            self.tags[track_index][idx] = [tag for tag in bar if tag not in tags]

    def remove_tags_at_index(self, tags, track_index, bar_index):
        """
        Remove tags at a specific index

        Parameters
        ----------
        tags : list[str]
            The tags to remove
        track_index : int
            The track index
        bar_index : int
            The bar index

        """
        self.tags[track_index][bar_index] = [tag for tag in self.tags[track_index][bar_index] if tag not in tags]

    def remove_tag_at_index(self, tag, track_index, bar_index):
        """
        Remove a tag at a specific index

        Parameters
        ----------
        tag : str
            The tag to remove
        track_index : int
            The track index
        bar_index : int
            The bar index

        """
        self.remove_tags_at_index([tag], track_index, bar_index)

    def remove_tags_for_bar(self, tags, bar_index):
        """
        Remove tags for a specific bar

        Parameters
        ----------
        tags : list[str]
            The tags to remove
        bar_index : int
            The bar index

        """
        for track in self.tags:
            track[bar_index] = [tag for tag in track[bar_index] if tag not in tags]

    def remove_tag_for_bar(self, tag, bar_index):
        """
        Remove a tag for a specific bar

        Parameters
        ----------
        tag : str
            The tag to remove
        bar_index : int
            The bar index

        """
        self.remove_tags_for_bar([tag], bar_index)


    def clear_tags(self):
        """
        Clear all tags
        """
        for track in self.tags:
            for bar in track:
                bar.clear()

    def clear_tags_for_track(self, track_index):
        """
        Clear all tags for a specific track

        Parameters
        ----------
        track_index : int
            The track index

        """
        for bar in self.tags[track_index]:
            bar.clear()

    def clear_tags_for_bar(self, bar_index):
        """
        Clear all tags for a specific bar

        Parameters
        ----------
        bar_index : int
            The bar index

        """
        for track in self.tags:
            track[bar_index].clear()

    def clear_tags_at_index(self, track_index, bar_index):
        """
        Clear all tags at a specific index

        Parameters
        ----------
        track_index : int
            The track index
        bar_index : int
            The bar index

        """
        self.tags[track_index][bar_index].clear()


    @property
    def shape(self):
        """
        Get the shape of the tag manager (should be the same as the score)
        """
        return len(self.tags), len(self.tags[0])

    def __len__(self):
        """
        Get the length of the tag manager (corresponding to the number of tracks)
        """
        return len(self.tags)

    def get_tags_at_index(self, track_index, bar_index):
        """
        Get the tags at a specific index

        Parameters
        ----------
        track_index : int
            The track index
        bar_index : int
            The bar index

        Returns
        -------
        list[str]
            The tags at the specified index

        """
        return self.tags[track_index][bar_index]

    def filter(self, function):
        """
        Filter the tags, keeping only the ones that match the function

        Parameters
        ----------
        function : function
            The function to filter the tags

        Returns
        -------
        TagManager
            The filtered tag manager

        """
        tags = [[list(filter(function, bar)) for bar in track] for track in self.tags]
        return TagManager(tags)

    def filter_remove(self, function):
        """
        Filter the tags, removing the ones that match the function

        Parameters
        ----------
        function : function
            The function to filter the tags

        Returns
        -------
        TagManager
            The filtered tag manager

        """
        tags = [[list(filter(lambda x: not function(x), bar)) for bar in track] for track in self.tags]
        return TagManager(tags)

    def __getitem__(self, item):
        """
        Get the tags for a specific item

        Parameters
        ----------
        item : int, slice or tuple
            The item to get

        Returns
        -------
        TagManager
            The sub tag manager

        """
        if isinstance(item, slice):
            return TagManager(self.tags[item])
        if isinstance(item, int):
            return TagManager([self.tags[item]])
        if isinstance(item, tuple):
            if len(item) != 2:
                raise ValueError("Item should be a tuple of length 2")
            first_dim, second_dim = item[0], item[1]
            tags_first_dim = self[first_dim].tags
            if isinstance(second_dim, slice):
                return TagManager([track[second_dim] for track in tags_first_dim])
            if isinstance(second_dim, int):
                return TagManager([[track[second_dim]] for track in tags_first_dim])


    def __setitem__(self, item, value):
        """
        Set the tags for a specific item.

        Parameters
        ----------
        item : int, slice, or tuple
            The item to set.
        value : TagManager, str, list[str], or list[list[str]]
            The value to set. Can be a TagManager with the same shape as the query,
            a single string (assign [value] to all cells of the query), a list of strings
            (assign value to the query), or a list of list of strings.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the value does not match the expected shape or type.
        """
        # If value is a list of list of list of strings, convert it to a TagManager
        if isinstance(value, list) and all(isinstance(v, list) and all(isinstance(s, list) for s in v) for v in value):
            value = TagManager(value)

        if isinstance(item, int):
            # Single track assignment
            if isinstance(value, TagManager):
                if len(value.tags) != 1 or len(value.tags[0]) != len(self.tags[item]):
                    raise ValueError(
                        "Shape mismatch: TagManager must have the same shape as the queried sub TagManager.")
                self.tags[item] = value.tags[0]
            elif isinstance(value, str):
                self.tags[item] = [[value] for _ in range(len(self.tags[item]))]
            elif isinstance(value, list):
                if all(isinstance(v, str) for v in value):
                    self.tags[item] = [value for _ in range(len(self.tags[item]))]
                elif all(isinstance(v, list) and all(isinstance(s, str) for s in v) for v in value):
                    if len(value) != len(self.tags[item]):
                        raise ValueError("Shape mismatch: list of lists must match the number of bars in the track.")
                    self.tags[item] = value
                else:
                    raise ValueError("Invalid value type: must be a list of strings or a list of list of strings.")
            elif value is None:
                self.tags[item] = [[] for _ in range(len(self.tags[item]))]
            else:
                raise ValueError(
                    "Invalid value type: must be a TagManager, string, list of strings, None, or list of list of strings.")
        elif isinstance(item, slice):
            # Slice assignment
            if isinstance(value, TagManager):
                if len(value.tags) != len(self.tags[item]):
                    raise ValueError(
                        "Shape mismatch: TagManager must have the same shape as the queried sub TagManager.")
                self.tags[item] = value.tags
            elif isinstance(value, str):
                for i in range(*item.indices(len(self.tags))):
                    self.tags[i] = [[value] for _ in range(len(self.tags[i]))]
            elif value is None:
                for i in range(*item.indices(len(self.tags))):
                    self.tags[i] = [[] for _ in range(len(self.tags[i]))]
            elif isinstance(value, list):
                if all(isinstance(v, str) for v in value):
                    for i in range(*item.indices(len(self.tags))):
                        self.tags[i] = [value for _ in range(len(self.tags[i]))]
                elif all(isinstance(v, list) and all(isinstance(s, str) for s in v) for v in value):
                    if len(value) != len(self.tags[item]):
                        raise ValueError("Shape mismatch: list of lists must match the number of tracks in the slice.")
                    self.tags[item] = value
                else:
                    raise ValueError("Invalid value type: must be a list of strings or a list of list of strings.")
            else:
                raise ValueError(
                    "Invalid value type: must be a TagManager, string, list of strings, or list of list of strings.")
        elif isinstance(item, tuple):
            if len(item) != 2:
                raise ValueError("Item should be a tuple of length 2")
            first_dim, second_dim = item[0], item[1]
            if isinstance(first_dim, int):
                if isinstance(second_dim, int):
                    # Single cell assignment
                    if isinstance(value, str):
                        self.tags[first_dim][second_dim] = [value]
                    elif isinstance(value, list) and all(isinstance(v, str) for v in value):
                        self.tags[first_dim][second_dim] = value
                    else:
                        raise ValueError("Invalid value type: must be a string or list of strings.")
                elif isinstance(second_dim, slice):
                    # Slice of bars in a single track
                    if isinstance(value, TagManager):
                        if len(value.tags) != 1 or len(value.tags[0]) != len(self.tags[first_dim][second_dim]):
                            raise ValueError(
                                "Shape mismatch: TagManager must have the same shape as the queried sub TagManager.")
                        self.tags[first_dim][second_dim] = value.tags[0]
                    elif isinstance(value, str):
                        for i in range(*second_dim.indices(len(self.tags[first_dim]))):
                            self.tags[first_dim][i] = [value]
                    elif isinstance(value, list):
                        if all(isinstance(v, str) for v in value):
                            for i in range(*second_dim.indices(len(self.tags[first_dim]))):
                                self.tags[first_dim][i] = value
                        elif all(isinstance(v, list) and all(isinstance(s, str) for s in v) for v in value):
                            if len(value) != len(self.tags[first_dim][second_dim]):
                                raise ValueError(
                                    "Shape mismatch: list of lists must match the number of bars in the slice.")
                            self.tags[first_dim][second_dim] = value
                        else:
                            raise ValueError(
                                "Invalid value type: must be a list of strings or a list of list of strings.")
                    elif value is None:
                        self.tags[first_dim][second_dim] = [[] for _ in self.tags[first_dim][second_dim]]
                    else:
                        raise ValueError(
                            "Invalid value type: must be a TagManager, string, None, list of strings, or list of list of strings.")
            elif isinstance(first_dim, slice):
                if isinstance(second_dim, int):
                    # Single bar across multiple tracks
                    if isinstance(value, TagManager):
                        if len(value.tags) != len(self.tags[first_dim]) or any(len(track) != 1 for track in value.tags):
                            raise ValueError(
                                "Shape mismatch: TagManager must have the same shape as the queried sub TagManager.")
                        for i, track in enumerate(self.tags[first_dim]):
                            track[second_dim] = value.tags[i][0]
                    elif isinstance(value, str):
                        for i in range(*first_dim.indices(len(self.tags))):
                            self.tags[i][second_dim] = [value]
                    elif value is None:
                        for i in range(*first_dim.indices(len(self.tags))):
                            self.tags[i][second_dim] = []
                    elif isinstance(value, list) and all(isinstance(v, str) for v in value):
                        for i in range(*first_dim.indices(len(self.tags))):
                            self.tags[i][second_dim] = value
                    else:
                        raise ValueError("Invalid value type: must be a TagManager, string, or list of strings.")
                elif isinstance(second_dim, slice):
                    # Slice of bars across multiple tracks
                    if isinstance(value, TagManager):
                        if len(value.tags) != len(self.tags[first_dim]) or any(
                                len(track) != len(self.tags[first_dim][0][second_dim]) for track in value.tags):
                            raise ValueError(
                                "Shape mismatch: TagManager must have the same shape as the queried sub TagManager.")
                        for i, track in enumerate(self.tags[first_dim]):
                            track[second_dim] = value.tags[i]
                    elif isinstance(value, str):
                        for i in range(*first_dim.indices(len(self.tags))):
                            for j in range(*second_dim.indices(len(self.tags[i]))):
                                self.tags[i][j] = [value]
                    elif value is None:
                        for i in range(*first_dim.indices(len(self.tags))):
                            for j in range(*second_dim.indices(len(self.tags[i]))):
                                self.tags[i][j] = []
                    elif isinstance(value, list):
                        if all(isinstance(v, str) for v in value):
                            for i in range(*first_dim.indices(len(self.tags))):
                                for j in range(*second_dim.indices(len(self.tags[i]))):
                                    self.tags[i][j] = value
                        elif all(isinstance(v, list) and all(isinstance(s, str) for s in v) for v in value):
                            if len(value) != len(self.tags[first_dim]) or any(
                                    len(v) != len(self.tags[first_dim][0][second_dim]) for v in value):
                                raise ValueError(
                                    "Shape mismatch: list of lists must match the number of tracks and bars in the slice.")
                            for i, track in enumerate(self.tags[first_dim]):
                                track[second_dim] = value[i]
                        else:
                            raise ValueError(
                                "Invalid value type: must be a list of strings or a list of list of strings.")
                    else:
                        raise ValueError(
                            "Invalid value type: must be a TagManager, string, list of strings, or list of list of strings.")
            else:
                raise ValueError("Invalid item type: must be an int, slice, or tuple of length 2.")
        else:
            raise ValueError("Invalid item type: must be an int, slice, or tuple of length 2.")