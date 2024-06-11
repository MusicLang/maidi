.. _models:


List of models
===============

You can use several models in integration with the API. Here is a list of current available models :

* **control_masking_large** : Latest model, with best performances masking model, can use `mask`, `tags` and `chords` arguments

* **masking_large** : Older masking model with good performances, can use `mask` argument but not `tags` and `chords`

* **masking_small** : Smaller masking model with lower performances but cheaper and faster, can use `mask` argument but not `tags` and `chords`

*Please note that all our models are limited to a 16-bar context for performance purposes in these examples.*


Usage
-----

Here is a simple example of how to use the API with the `control_masking_large` model ::

    import os
    from maidi import MidiScore
    from maidi import instrument
    from maidi.integrations.api import MusicLangAPI

    chosen_model = "control_masking_large" # Choose model here
    score = MidiScore.from_empty(
        instruments=[instrument.PIANO], nb_bars=4, ts=(4, 4), tempo=120
    )
    mask, tags, chords = score.get_empty_controls(prevent_silence=True)
    mask[:, :] = 1  # Regenerate everything in the score

    # Call the musiclang API to predict the score
    api = MusicLangAPI(os.getenv("API_URL"), os.getenv("API_KEY"), verbose=True)
    predicted_score = api.predict(score,
        model=model,  # Use this argument to choose the model
        mask, tags=tags, chords=chords, async_mode=False, polling_interval=5
    )
    predicted_score.write("predicted_score.mid")
