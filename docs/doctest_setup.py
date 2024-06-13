from unittest.mock import patch

def mock_predict_with_api(self, score, mask, model="control_masking_large", temperature=0.95, async_mode=False, polling_interval=1, chords=None, tags=None, **prediction_kwargs):
    # Return the score parameter as is
    return score


def mock_from_task_id(self, task_id, polling_interval=1, timeout=3000):
    from maidi import MidiScore
    return MidiScore.from_empty(['piano', 'flute'], nb_bars=4, ts=(4, 4), tempo=120)
def mock_write(self, filename):
    # Do nothing
    pass

def mock_from_midi(filename):
    from maidi import MidiScore
    return MidiScore.from_empty(['piano', 'flute'], nb_bars=4, ts=(4, 4), tempo=120)

def setup_doctest(doctest_namespace):
    # Patch the specific method in the maidi.MusicLangAPI class
    patcher = patch('maidi.integrations.api.MusicLangAPI._predict_with_api', mock_predict_with_api)
    patcher.start()

    patcher_write = patch('maidi.MidiScore.write', mock_write)
    patcher_write.start()

    patcher_from_midi = patch('maidi.MidiScore.from_midi', mock_from_midi)
    patcher_from_midi.start()

    patcher_from_task_id = patch('maidi.integrations.api.MusicLangAPI.from_task_id', mock_from_task_id)
    patcher_from_task_id.start()

    import atexit
    atexit.register(patcher.stop)
    atexit.register(patcher_write.stop)
    atexit.register(patcher_from_midi.stop)
    atexit.register(patcher_from_task_id.stop)
# -----------------------------------------------------------------------------