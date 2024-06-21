import pytest
from unittest.mock import MagicMock, patch

# Mocking the ChordManager and TagManager classes
class MockChordManager:
    def __init__(self, chords):
        self.chords = chords

    def __len__(self):
        return len(self.chords)

    def __getitem__(self, item):
        return self.chords[item]

class MockTagManager:
    def __init__(self, tags):
        self.tags = tags

    def get_tags_at_index(self, track_index, bar_index):
        return self.tags[track_index][bar_index]

    def __len__(self):
        return len(self.tags)

    def __getitem__(self, item):
        return self.tags[item]


# Mocking the ScoreTagger class and its method
class MockScoreTagger:
    @staticmethod
    def get_base_tagger():
        return MockScoreTagger()

    def tag_score(self, predicted_score):
        return predicted_score

# Patching the imports in the GenerationMetric class
@patch('maidi.TagManager', MockTagManager)
@patch('maidi.ChordManager', MockChordManager)
@patch('maidi.analysis.ScoreTagger', MockScoreTagger)
def test_tags_recall():
    from maidi.analysis.metrics import GenerationMetric  # Replace 'your_module' with the actual module name

    initial_tags = [
        [['tag1', 'tag2'], ['tag3']],
        [['tag4'], ['tag5', 'tag6']]
    ]
    predicted_tags = [
        [['tag1'], ['tag3', 'tag7']],
        [['tag4'], ['tag5']]
    ]
    predicted_score = MagicMock()
    predicted_score.get_tags_at_index = lambda i, j: predicted_tags[i][j]

    metric = GenerationMetric(initial_tags, initial_tags, predicted_score)
    metric.new_tags = MockTagManager(predicted_tags)


    recall = metric.tags_recall()
    assert recall == 4 / 6  # 4 recalled tags out of 6 total tags

@patch('maidi.TagManager', MockTagManager)
@patch('maidi.ChordManager', MockChordManager)
@patch('maidi.analysis.ScoreTagger', MockScoreTagger)
def test_tag_recall_for_index():
    from maidi.analysis.metrics import GenerationMetric

    initial_tags = [
        [['tag1', 'tag2'], ['tag3']],
        [['tag4'], ['tag5', 'tag6']]
    ]
    predicted_tags = [
        [['tag1'], ['tag3', 'tag7']],
        [['tag4'], ['tag5']]
    ]
    predicted_score = MagicMock()
    predicted_score.get_tags_at_index = lambda i, j: predicted_tags[i][j]

    metric = GenerationMetric(initial_tags, initial_tags, predicted_score)
    metric.new_tags = MockTagManager(predicted_tags)

    recall = metric.tag_recall_for_index(0, 0)
    assert recall == 1 / 2  # 1 recalled tag out of 2 total tags

@patch('maidi.TagManager', MockTagManager)
@patch('maidi.ChordManager', MockChordManager)
@patch('maidi.analysis.ScoreTagger', MockScoreTagger)
def test_chords_recall():
    from maidi.analysis.metrics import GenerationMetric

    initial_chords = ['C', 'G', 'Am', 'F']
    predicted_chords = ['C', 'G', 'Em', 'F']
    predicted_score = MagicMock()
    predicted_score.get_chords = lambda: predicted_chords

    metric = GenerationMetric(initial_chords, initial_chords, predicted_score)
    metric.new_chords = predicted_chords
    recall = metric.chords_recall()
    assert recall == 3 / 4  # 3 recalled chords out of 4 total chords

@patch('maidi.TagManager', MockTagManager)
@patch('maidi.ChordManager', MockChordManager)
@patch('maidi.analysis.ScoreTagger', MockScoreTagger)
def test_global_recall():
    from maidi.analysis.metrics import GenerationMetric

    initial_tags = [
        [['tag1', 'tag2'], ['tag3']],
        [['tag4'], ['tag5', 'tag6']]
    ]
    predicted_tags = [
        [['tag1'], ['tag3', 'tag7']],
        [['tag4'], ['tag5']]
    ]
    initial_chords = ['C', 'G', 'Am', 'F']
    predicted_chords = ['C', 'G', 'Em', 'F']
    predicted_score = MagicMock()
    predicted_score.get_tags_at_index = lambda i, j: predicted_tags[i][j]
    predicted_score.get_chords = lambda: predicted_chords

    metric = GenerationMetric(initial_chords, initial_tags, predicted_score)
    metric.new_tags = MockTagManager(predicted_tags)
    metric.new_chords = predicted_chords
    global_recall = metric.global_recall()
    expected_recall = (3 / 4) * 0.7 + (4 / 6) * 0.3  # Weighted average of chords and tags recall
    assert global_recall == expected_recall


@patch('maidi.TagManager', MockTagManager)
@patch('maidi.ChordManager', MockChordManager)
@patch('maidi.analysis.ScoreTagger', MockScoreTagger)
def test_full_recall_report():
    from maidi.analysis.metrics import GenerationMetric

    initial_tags = [
        [['tag1', 'tag2'], ['tag3']],
        [['tag4'], ['tag5', 'tag6']]
    ]
    predicted_tags = [
        [['tag1'], ['tag3', 'tag7']],
        [['tag4'], ['tag5']]
    ]
    initial_chords = ['C', 'A']
    predicted_chords = ['C', 'G']
    predicted_score = MagicMock()
    predicted_score.get_tags_at_index = lambda i, j: predicted_tags[i][j]
    predicted_score.get_chords = lambda: predicted_chords

    metric = GenerationMetric(initial_chords, initial_tags, predicted_score)
    metric.new_tags = MockTagManager(predicted_tags)
    metric.new_chords = predicted_chords
    recall_report = metric.full_recall_report()

    expected_tags_recall = [
        [1 / 2,  # Track 0, Bar 0
        1 / 1],  # Track 0, Bar 1
        [1 / 1,  # Track 1, Bar 0
        1 / 2]  # Track 1, Bar 1
    ]
    expected_chords_recall = [
        1 / 1,  # Bar 0
        0 / 1,  # Bar 1
    ]

    assert recall_report['tags'] == expected_tags_recall
    assert recall_report['chords'] == expected_chords_recall

@patch('maidi.TagManager', MockTagManager)
@patch('maidi.ChordManager', MockChordManager)
@patch('maidi.analysis.ScoreTagger', MockScoreTagger)
def test_chords_recall():
    from maidi.analysis.metrics import GenerationMetric

    initial_chords = ['C', 'G', 'Am', 'F']
    predicted_chords = ['C', 'G', 'Em', 'F']
    predicted_score = MagicMock()
    predicted_score.get_chords = lambda: predicted_chords

    metric = GenerationMetric(initial_chords, initial_chords, predicted_score)

    metric.new_chords = predicted_chords


    recall = metric.chords_recall()
    assert recall == 3 / 4  # 3 recalled chords out of 4 total chords


import pytest
from unittest.mock import MagicMock, patch

# Mocking the ChordManager and TagManager classes
class MockChordManager:
    def __init__(self, chords):
        self.chords = chords

    def __len__(self):
        return len(self.chords)

    def __getitem__(self, item):
        return self.chords[item]


# Patching the imports in the GenerationMetric class
@patch('maidi.TagManager', MockTagManager)
@patch('maidi.ChordManager', MockChordManager)
@patch('maidi.analysis.ScoreTagger', MockScoreTagger)
def test_tag_and_chord_recalls():
    from maidi.analysis.metrics import GenerationMetric  # Replace 'your_module' with the actual module name

    initial_tags = [
        [['tag1', 'tag2'], ['tag3', 'tag1']],
        [['tag4'], ['tag5', 'tag6']]
    ]
    predicted_tags = [
        [['tag1'], ['tag3', 'tag7']],
        [['tag4'], ['tag5']]
    ]
    initial_chords = [('C', 'G', 'major', '7'), ('G', 'D', 'minor', '7')]
    predicted_chords = [('C', 'G', 'major', '7'), ('G', 'D', 'major', '7')]

    predicted_score = MagicMock()
    predicted_score.get_tags_at_index = lambda i, j: predicted_tags[i][j]
    predicted_score.get_chords = lambda: predicted_chords

    metric = GenerationMetric(initial_chords, initial_tags, predicted_score)
    metric.new_tags = MockTagManager(predicted_tags)
    metric.new_chords = MockChordManager(predicted_chords)

    tags_dict_recall, chords_dict_recall = metric.tag_and_chord_recalls()

    expected_tags_dict_recall = {
        'tag1': [1, 2],
        'tag2': [0, 1],
        'tag3': [1, 1],
        'tag4': [1, 1],
        'tag5': [1, 1],
        'tag6': [0, 1]
    }
    expected_chords_dict_recall = {
        ('C', 'G', 'major', '7'): [1, 1],
        ('G', 'D', 'minor', '7'): [0, 1]
    }

    assert tags_dict_recall == expected_tags_dict_recall
    assert chords_dict_recall == expected_chords_dict_recall


if __name__ == "__main__":
    pytest.main()