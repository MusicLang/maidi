import pytest
from maidi.analysis.control_features import (
    get_density_tags,

)

from maidi.analysis.control_features.density import (
    get_density_value,
    get_density,
    get_tags_names, DensityTagsProvider,
)


def test_get_density_value():
    """ """
    assert get_density_value(0.2) == "LOWEST"
    assert get_density_value(0.4) == "LOWER"
    assert get_density_value(1.5) == "LOW"
    assert get_density_value(3.0) == "MEDIUM_LOW"
    assert get_density_value(5.0) == "MEDIUM"
    assert get_density_value(7.0) == "HIGH"
    assert get_density_value(8.5) == "VERY_HIGH"


def test_get_density():
    """ """
    # Test case with no notes
    assert get_density([], 4) == "LOWEST"

    # Test case with notes leading to 'LOWEST' density
    notes = [(0, 1), (2, 3), (4, 5)]
    assert get_density(notes, 16) == "LOWEST"  # density = 3/16 = 0.1875

    # Test case with notes leading to 'LOWER' density
    notes = [(0, 1), (2, 3), (4, 5)]
    assert get_density(notes, 6) == "LOW"  # density = 3/6 = 0.5

    # Test case with notes leading to 'LOW' density
    notes = [(0, 1), (0.5, 1.5), (1, 2)]
    assert get_density(notes, 2) == "LOW"  # density = 3/2 = 1.5

    # Test case with notes leading to 'MEDIUM_LOW' density
    notes = [(0, 1), (0.25, 1.25), (0.5, 1.5), (0.75, 1.75)]
    assert get_density(notes, 2) == "MEDIUM_LOW"  # density = 4/2 = 2

    # Test case with notes leading to 'MEDIUM' density
    notes = [(0, 1), (0.2, 1.2), (0.4, 1.4), (0.6, 1.6), (0.8, 1.8), (1, 2)]
    assert get_density(notes, 2) == "MEDIUM_LOW"  # density = 6/2 = 3

    # Test case with notes leading to 'HIGH' density
    notes = [
        (0, 0.5),
        (0.1, 0.6),
        (0.2, 0.7),
        (0.3, 0.8),
        (0.4, 0.9),
        (0.5, 1),
        (0.6, 1.1),
        (0.7, 1.2),
    ]
    assert get_density(notes, 2) == "MEDIUM"  # density = 8/2 = 4

    # Test case with notes leading to 'VERY_HIGH' density
    notes = [
        (0, 0.25),
        (0.1, 0.35),
        (0.2, 0.45),
        (0.3, 0.55),
        (0.4, 0.65),
        (0.5, 0.75),
        (0.6, 0.85),
        (0.7, 0.95),
        (0.8, 1.05),
        (0.9, 1.15),
    ]
    assert get_density(notes, 2) == "MEDIUM"  # density = 10/2 = 5


def test_get_token_names():
    """ """
    expected_token_names = [
        "CONTROL_DENSITY__LOWEST",
        "CONTROL_DENSITY__LOWER",
        "CONTROL_DENSITY__LOW",
        "CONTROL_DENSITY__MEDIUM_LOW",
        "CONTROL_DENSITY__MEDIUM",
        "CONTROL_DENSITY__HIGH",
        "CONTROL_DENSITY__VERY_HIGH",
    ]
    assert get_tags_names() == expected_token_names


def test_density_provider_tags_list():
    """ """
    provider = DensityTagsProvider()
    assert provider.get_tags_list() == get_tags_names()


if __name__ == "__main__":
    pytest.main()
