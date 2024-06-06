# Contributing to the Project

M(ai)di is an open source project that aims to highlight the capabilities and usefulness of the Symbolic Music GenAI. 

We welcome contributions to the project as long as they fit the main philosophy of the project:

## Our mission:

- **Integration of symbolic music open source tools**: It can be a model or any algorithm that generates music in a symbolic format. We are open to any kind of integration that could help users generate music.
- 
- **Integration of symbolic music APIs**: If you have an API that process midi files, we would love to integrate it into the project. It can be a free or a paid API. This integration would not only allow you to gain visibility by promoting your API with a high-level interface but also extend the catalog of features we can propose to users. While we don't focus on pure audio here, we are open to any kind of integration that could help transcribe audio to MIDI or vice versa.

- **Composition Helpers and Tools**: If you have a feature that would assist with algorithmic composition of music, we are definitely interested.

- **Interface Improvements**: If you have an idea to enhance how MIDI files are handled and/or the main data structures, we would love to hear about it. We aim to make the library as easy to use as possible while ensuring it fits most GenAI use cases.

- **Bug Fixes**: If you find a bug, please report it in the issues section. If you can fix it, please submit a pull request.

## What we won't accept:

- **Pure Audio Features**: We are not focusing on audio features here; our focus is on symbolic music generation.

- **Anything Related to Model Training or Tokenizers**: We strictly focus on providing ready-to-use services for symbolic music manipulation. We only want what is related to musical knowledge. This excludes tokenizers, which are too low-level for our use case. If you want to contribute to a tokenizer library, please check [MidiTok](https://github.com/Natooz/MidiTok).

- **Code Optimizations that Make the Code Harder to Read**: We prefer readable code over optimized code. We want the code to be as easy to understand as possible.

- **Features that are Not Related to Symbolic Music Generation**: While it doesn't necessarily have to be AI, it must be related to music generation.

# Contributing Guidelines

In more technical terms, here are the guidelines to follow when contributing to the project:

- **Code Style**: We adhere to the [black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html) code style.

- **Documentation**: We use the [numpy](https://numpydoc.readthedocs.io/en/latest/format.html) documentation style.

- **Testing**: We use the [pytest](https://docs.pytest.org/en/stable/) testing framework.

- **Code Quality**: We employ [flake8](https://flake8.pycqa.org/en/latest/) for code quality checks.

- **Code Coverage**: We utilize [coverage](https://coverage.readthedocs.io/en/coverage-5.5/) for code coverage checks.

- **Use of asynchronous APIs**: If your API takes a long time to respond, please make it asynchronous, see how we have implemented the [MusicLang API](https://api.musiclang.io/documentation) for example.

Please ensure to adhere to these guidelines when contributing to the project; otherwise, your pull request might be rejected.
