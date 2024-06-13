 rm -rf docs/_build
 sphinx-build -M html docs  docs/_build
 sphinx-build -b doctest docs docs/_build/doctest