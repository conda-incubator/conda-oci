import re

from conda.models.version import VersionOrder

# see https://github.com/opencontainers/distribution-spec/blob/main/spec.md#pulling-manifests
VALID_NAME_RE = re.compile(
    r"^[a-z0-9]+((\.|_|__|-+)[a-z0-9]+)*(\/[a-z0-9]+((\.|_|__|-+)[a-z0-9]+)*)*$"
)
VALID_TAG_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9._-]{0,127}$")

# see conda/schemas
VALID_CONDA_PKG_NAME_RE = re.compile(
    r"^(([a-z0-9])|([a-z0-9_](?!_)))[._-]?([a-z0-9]+(\.|-|_|$))*$"
)
VALID_CONDA_CHANNEL_RE = re.compile(r"^[a-z0-9]+((-|_|.)[a-z0-9]+)*$")
VALID_CONDA_SUBDIR_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VALID_CONDA_LABEL_RE = re.compile(r"^[a-zA-Z][0-9a-zA-Z_\-\.\/:\s]*")
VALID_CONDA_BUILD_STRING_RE = re.compile(r"^[a-zA-Z0-9_\.+]+$")


def separate_channel_label(channel_label):
    parts = channel_label.split("/")
    if any(part == "label" for part in parts) and parts[-1] != "label":
        # get last index of part that is "label"
        for i, part in enumerate(parts):
            if part == "label":
                label_index = i
        channel = "/".join(parts[:label_index])
        label = "/".join(parts[label_index + 1 :])
    else:
        channel = channel_label
        label = None

    return channel, label


def is_valid_oci_dist(dist):
    """Check if an oci dist name is valid."""
    name, tag = dist.rsplit(":", maxsplit=1)

    if not VALID_TAG_RE.match(tag):
        return False

    if name.startswith("oci://"):
        name = name[6:]

    if len(name) > 255:
        return False

    if not VALID_NAME_RE.match(name):
        return False

    return True


def is_valid_conda_dist(dist):
    """Check if a conda dist is valid."""

    if dist.endswith(".tar.bz2"):
        dist = dist[:-8]
    elif dist.endswith(".conda"):
        dist = dist[:-6]

    name, ver, build = dist.rsplit("-", maxsplit=2)
    if "/" in name:
        channel, subdir, name = name.rsplit("/", maxsplit=2)
    else:
        channel = None
        subdir = None

    if channel is not None:
        channel, label = separate_channel_label(channel)
    else:
        label = None

    if channel is not None and not VALID_CONDA_CHANNEL_RE.match(channel):
        return False

    if label is not None and not VALID_CONDA_LABEL_RE.match(label):
        return False

    if subdir is not None and not VALID_CONDA_SUBDIR_RE.match(subdir):
        return False

    if not VALID_CONDA_PKG_NAME_RE.match(name):
        return False

    if not VALID_CONDA_BUILD_STRING_RE.match(build):
        return False

    try:
        VersionOrder(ver)
    except Exception:
        return False

    return True
