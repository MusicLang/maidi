About M(AI)DI
===============

.. image:: ../../assets/logo2.png
  :width: 400
  :alt: Maidi logo


M(ai)di is an open source python library that aims to highlight the capabilities and usefulness of the **Symbolic Music GenAI**.
It interfaces with the best symbolic music AI models and APIs to **accelerate AI integration in music tech products**.
It came from the realization that artists need to manipulate MIDI and not only audio in their composition workflow but tools are lacking in this area.

So here we are, providing a simple and efficient way to manipulate midi files and integrate with music AI models.
In a few lines of code you will be able to parse, analyze and generate midi files with the best music AI models available.

**Here is where M(ai)di shines:**

- **Midi Files Manipulation**: Load, save, edit, merge and analyze midi files with ease.
- **Music AI Models Integration**: Integrate with the best music AI models and APIs to generate music.
- **Automatic MIDI tagging**: Get the chords, tempo, time signature, and many other musical features for each bar/instrument of the midi file.

*Disclaimer : We really focus on processing midi files and model inference calls. We don't implement audio features, neither model training, neither tokenization.*

Getting Started
===============

Installation
------------
To install the package, you can use pip::

    pip install maidi


Or to get the latest version from the repository, you can use::

    pip install git+github.com/MusicLang/maidi.git


Hello World script
-------------------

A simple code snippet to load and analyze a midi file ::

    from maidi import MidiScore, ScoreTagger, midi_library
    from maidi.analysis import tags_providers

    score = MidiScore.from_midi(midi_library.get_midi_file('drum_and_bass'))

    tagger = ScoreTagger(
        [
            tags_providers.DensityTagsProvider(),
            tags_providers.MinMaxPolyphonyTagsProvider(),
            tags_providers.MinMaxRegisterTagsProvider(),
            tags_providers.SpecialNotesTagsProvider(),
        ]
    )

    tags = tagger.tag_score(score)
    chords = score.get_chords_prompt()
    print(tags)
    print(chords)

Integrations
============

The power of maidi comes from its ability to integrate with the best music AI models and APIs.

Please refer to the :ref:`integrations` section for more details on how to integrate with music AI models.

Contributing
============

We welcome contributions to the project as long as it fits its main philosophy :

- Manipulate midi files in some ways
- Integrate with music AI models (inference & symbolic only)

Please read :ref:`contributing` for details on our guidelines.

License
=========

This package is licensed under the Apache License 2.0
