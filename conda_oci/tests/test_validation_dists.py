import pytest

from conda_oci.validation import (
    is_valid_oci_dist,
)


@pytest.mark.parametrize(
    "dist,is_valid",
    [
        ("f" * 300 + ":1.0.0-1", False),
        ("_f" + ":1.0.0-1", False),
        ("_f" + ":1.0.0-1" + "4" * 300, False),
        ("b__f" + ":1.0.0-1", True),
        ("B__f" + ":1.0.0-1", False),
        ("b__f___g" + ":1.0.0-1", False),
    ],
)
def test_is_valid_oci_dist(dist, is_valid):
    assert is_valid_oci_dist(dist) is is_valid
