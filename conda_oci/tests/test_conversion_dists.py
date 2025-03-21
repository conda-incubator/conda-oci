import pytest

from conda_oci.conversion import (
    decode_oci_dist_to_conda_dist,
    decode_pkg_from_oci,
    decode_version_build_from_oci,
    encode_conda_dist_to_oci_dist,
    encode_pkg_to_oci,
    encode_version_build_to_oci,
)
from conda_oci.validation import (
    VALID_CONDA_LABEL_RE,
    VALID_TAG_RE,
    is_valid_conda_dist,
    is_valid_oci_dist,
)


@pytest.mark.parametrize(
    "name,ename",
    [
        ("foo", "cfoo"),
        ("_foo", "c_foo"),
        ("bar", "cbar"),
        ("_bar", "c_bar"),
        ("zbar", "czbar"),
        ("z_bar", "cz_bar"),
        ("_zbar", "c_zbar"),
        ("_z_bar", "c_z_bar"),
        ("_foo_bar", "c_foo_bar"),
        ("foo_bar", "cfoo_bar"),
        ("foo_zbar", "cfoo_zbar"),
        ("foo_z_bar", "cfoo_z_bar"),
    ],
)
def test_encode_decode_pkg_to_oci(name, ename):
    assert encode_pkg_to_oci(name) == ename
    assert decode_pkg_from_oci(ename) == name


@pytest.mark.parametrize(
    "vb,ebv",
    [
        ("1.0.0", "1.0.0"),
        ("1.0.0_1", "1.0.0__1"),
        ("1.0.0+1", "1.0.0_P1"),
        ("1.0.0!1", "1.0.0_N1"),
        ("1.0.0+1_1", "1.0.0_P1__1"),
        ("1.0.0+1!1", "1.0.0_P1_N1"),
        ("1.0.0_+1_1", "1.0.0___P1__1"),
    ],
)
def test_encode_decode_label_version_build_to_oci(vb, ebv):
    assert encode_version_build_to_oci(vb) == ebv
    assert decode_version_build_from_oci(ebv) == vb
    if vb.startswith("blah"):
        assert VALID_CONDA_LABEL_RE.match(vb) is not None
    assert VALID_TAG_RE.match(ebv) is not None


@pytest.mark.parametrize(
    "dist,oci_dist",
    [
        ("foo-1.0.0-1.conda", "cfoo:1.0.0-1"),
        ("foo-1.0.0_1-0", "cfoo:1.0.0__1-0"),
        ("foo-1.0.0+1-h34243_0", "cfoo:1.0.0_P1-h34243__0"),
        ("foo-1.0.0!1-h34243_0", "cfoo:1.0.0_N1-h34243__0"),
        ("foo-1.0.01-h34243_0.tar.bz2", "cfoo:1.0.01-h34243__0"),
        ("foo-1.0.0+1_1-h34243_0", "cfoo:1.0.0_P1__1-h34243__0"),
        ("foo-1!1.0.0-h34243_0", "cfoo:1_N1.0.0-h34243__0"),
        ("_foo-1.0.0_+1_1-h34243_0", "c_foo:1.0.0___P1__1-h34243__0"),
        ("cfoo-1.0.0_+1_1-h34243_0", "ccfoo:1.0.0___P1__1-h34243__0"),
        ("z_foo-1.0.0_+1_1-h34243_0", "cz_foo:1.0.0___P1__1-h34243__0"),
        ("cz_foo-1.0.0_+1_1-h34243_0", "ccz_foo:1.0.0___P1__1-h34243__0"),
    ],
)
def test_encode_conda_dist_to_oci_dist(dist, oci_dist):
    assert (
        encode_conda_dist_to_oci_dist("conda-forge/linux-64/" + dist)
        == "conda-forge/linux-64/" + oci_dist
    )
    assert is_valid_oci_dist("conda-forge/linux-64/" + oci_dist)


@pytest.mark.parametrize(
    "conda_dist,oci_dist",
    [
        (
            "conda-forge/label/test/linux-64/gdal-2.3.3-py27hf242f0b_1",
            "conda-forge/label/test/linux-64/cgdal:2.3.3-py27hf242f0b__1",
        ),
        (
            "conda-forge/label/test/linux-64/_gdal-2.3.3-py27hf242f0b_1",
            "conda-forge/label/test/linux-64/c_gdal:2.3.3-py27hf242f0b__1",
        ),
        (
            "conda-forge/label/test/blah/linux-64/_gdal-2.3.3-py27hf242f0b_1",
            "conda-forge/label/test/blah/linux-64/c_gdal:2.3.3-py27hf242f0b__1",
        ),
        (
            "conda-forge/label/test/blah/linux-64/_gdal-2.3.3-py27hf242f0b_1",
            "conda-forge/label/test/blah/linux-64/c_gdal:2.3.3-py27hf242f0b__1",
        ),
        (
            "conda-forge/linux-64/gdal-2.3.3-py27hf242f0b_1",
            "conda-forge/linux-64/cgdal:2.3.3-py27hf242f0b__1",
        ),
        (
            "conda-forge/linux-64/_gdal-2.3.3-py27hf242f0b_1",
            "conda-forge/linux-64/c_gdal:2.3.3-py27hf242f0b__1",
        ),
        (
            "conda-forge/linux-64/" + "g" * 300 + "-2.3.3-py27hf242f0b_1",
            "conda-forge/linux-64/h42d944d006b5831a1be5e7456647dbbb0c497135:h226b5fd99dd083cf39532c3411fb71c88c5411f3",
        ),
        (
            "conda-forge/linux-64/g" + "-" + "2" * 300 + "2.3.3-py27hf242f0b_1",
            "conda-forge/linux-64/hbb0b6647e93b6fb3593e649f301d6c4b49990a8a:h7d81d06b602eab7ca94f7dccdbbe5faa7aadedb8",
        ),
    ],
)
def test_encode_decode_conda_dist_to_oci_dist(conda_dist, oci_dist):
    assert encode_conda_dist_to_oci_dist(conda_dist) == oci_dist
    assert is_valid_oci_dist(oci_dist)
    assert is_valid_conda_dist(conda_dist)
    if oci_dist.split("/")[-1][0] == "h" or oci_dist.split(":")[1][0] == "h":
        with pytest.raises(ValueError):
            decode_oci_dist_to_conda_dist(oci_dist)
    else:
        if conda_dist.count("/") == 3:
            assert decode_oci_dist_to_conda_dist(oci_dist) == conda_dist
        else:
            assert (
                decode_oci_dist_to_conda_dist(oci_dist, urlencode_label=False)
                == conda_dist
            )
