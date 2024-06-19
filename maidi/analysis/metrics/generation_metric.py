

class GenerationMetric:

    """
    This class is used to evaluate the quality of a generated score.
    It can be used to select score on a best fit basis or regenerate specific bars or tracks that are not satisfying.
    """

    def __init__(self, chords, tags, predicted_score):
        from maidi import TagManager, ChordManager
        self.chords = ChordManager(chords)
        self.tags = TagManager(tags)
        self.predicted_score = predicted_score
        self.new_tags = self.get_tagger().tag_score(self.predicted_score)
        self.new_chords = ChordManager(self.predicted_score.get_chords())

    @classmethod
    def get_tagger(cls):
        from maidi.analysis import ScoreTagger
        return ScoreTagger.get_base_tagger()

    def tags_recall(self):
        """
        Compute the recall of the tags in the predicted score.
        (portion of the initial tags that are in the predicted tags for each bars of each track)
        """
        initial_tags = self.tags
        recalled_tags = 0
        total_tags = 0
        for i in range(len(self.new_tags)):
            for j in range(len(self.new_tags[i])):
                new_tags_locals = self.new_tags.get_tags_at_index(i, j)
                initial_tags_local = initial_tags.get_tags_at_index(i, j)
                recalled_tags += len(set(new_tags_locals).intersection(initial_tags_local))
                total_tags += len(initial_tags_local)
        return recalled_tags / total_tags


    def tag_recall_for_index(self, track_index, bar_index):
        """
        Compute the recall of the tags in the predicted score for a specific track and bar.
        (portion of the initial tags that are in the predicted tags for a specific track and bar)

        Parameters
        ----------
        track_index : int
            The index of the track to evaluate.

        bar_index : int
            The index of the bar to evaluate.
        """
        initial_tags = self.tags

        recalled_tags = 0
        total_tags = 0
        new_tags_locals = self.new_tags.get_tags_at_index(track_index, bar_index)
        initial_tags_local = initial_tags.get_tags_at_index(track_index, bar_index)
        recalled_tags += len(set(new_tags_locals).intersection(initial_tags_local))
        total_tags += len(initial_tags_local)
        if total_tags == 0:
            return 1.0

        return recalled_tags / total_tags


    def chord_recall_for_index(self, bar_index):
        """
        Compute the recall of the chords in the predicted score for a specific bar.
        (portion of the initial chords that are in the predicted chords for a specific bar)

        Parameters
        ----------
        bar_index : int
            The index of the bar to evaluate.
        """
        initial_chord = self.chords[bar_index]
        new_chord = self.new_chords[bar_index]
        if initial_chord == new_chord:
            return 1.0
        return 0.0


    def full_recall_report(self):
        """
        Compute the recall of the tags and chords in the predicted score for each track and bar.
        Return a dictionary with two keys : 'tags' and 'chords' containing the recall for each track and bar.

        Returns
        -------
        dict
            A dictionary containing the recall for each track and bar.
        """
        recall_report = {'tags': [], 'chords': []}
        for i in range(len(self.new_tags)):
            track_tags = []
            for j in range(len(self.new_tags.tags[i])):
                track_tags.append(self.tag_recall_for_index(i, j))
                if i == 0:
                    recall_report['chords'].append(self.chord_recall_for_index(j))
            recall_report['tags'].append(track_tags)
        return recall_report


    def chords_recall(self):
        """
        Compute the recall of the chords in the predicted score.
        (portion of the initial chords that are in the predicted chords)
        """
        chords = self.chords
        recalled_chords = 0
        total_chords = 0
        for i in range(len(chords)):
            initial_chord = chords[i]
            new_chord = self.new_chords[i]
            if initial_chord == new_chord:
                recalled_chords += 1
            total_chords += 1

        if total_chords == 0:
            return 1.0

        return recalled_chords / total_chords

    def global_recall(self, weight_chords=0.7, weight_tags=0.3):
        """
        Compute the global recall of the predicted score.
        The global recall is a weighted average of the recall of the tags and the recall of the chords.

        Parameters
        ----------
        weight_chords : float, optional
            The weight of the recall of the chords in the global recall. The default is 0.7.

        weight_tags : float, optional
            The weight of the recall of the tags in the global recall. The default is 0.3.
        """

        recall_chords = self.chords_recall()
        recall_tags = self.tags_recall()

        return recall_chords * weight_chords + recall_tags * weight_tags
