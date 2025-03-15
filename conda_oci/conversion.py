import hashlib


def encode_pkg_to_oci(name):
    """Encode a conda package name to an OCI image name."""
    return "c" + name


def decode_pkg_from_oci(name):
    """Decode an OCI image name to a conda package name."""
    return name[1:]


def encode_version_build_to_oci(version_or_build):
    """Encode a conda package version or build string to an OCI image tag."""
    return version_or_build.replace("_", "__").replace("+", "_P").replace("!", "_N")


def decode_version_build_from_oci(version_or_build):
    """Decode an OCI image tag to a conda package version or build string."""
    return version_or_build.replace("_N", "!").replace("_P", "+").replace("__", "_")


def encode_conda_dist_to_oci_dist(dist):
    """Convert a conda package name to an OCI image name."""

    if dist.endswith(".tar.bz2"):
        dist = dist[:-8]
    elif dist.endswith(".conda"):
        dist = dist[:-6]

    name, ver, build = dist.rsplit("-", maxsplit=2)
    channel, subdir, name = name.rsplit("/", maxsplit=2)

    name = encode_pkg_to_oci(name)
    ver = encode_version_build_to_oci(ver)
    build = encode_version_build_to_oci(build)

    channel_subdir = f"{channel}/{subdir}"
    oci_name = f"{channel_subdir}/{name}"
    oci_tag = f"{ver}-{build}"

    if len(oci_name) > 128 or len(oci_tag) > 128:
        oci_tag = "h" + hashlib.sha1(oci_tag.encode("ascii")).hexdigest()
        oci_name = (
            channel_subdir + "/h" + hashlib.sha1(name.encode("ascii")).hexdigest()
        )

    return f"{oci_name}:{oci_tag}"


def decode_oci_dist_to_conda_dist(dist, urlencode_label=True):
    """Convert an OCI image name to a conda package name."""

    if dist.startswith("oci://"):
        # assume name is oci://<registry>/<image>:tag
        # strip out oci:// and the registry
        dist = dist[6:]
        dist = dist.split("/", maxsplit=1)[-1]

    name, tag = dist.rsplit(":", maxsplit=1)
    if tag.startswith("h"):
        raise ValueError(
            "OCI dist names with hashed components cannot be "
            "decoded. Read the image metadata to find the "
            "conda package name."
        )

    name_parts = name.rsplit("/", maxsplit=2)
    if len(name_parts) != 3:
        raise ValueError(
            "channel and subdir information must be "
            "prepended in the format <channel>/<subdir>"
            f"/<oci dist>. Got {name} which cannot be interpreted."
        )
    channel, subdir, name = name_parts
    if name.startswith("h"):
        raise ValueError(
            "OCI dist names with hashed components cannot be "
            "decoded. Read the image metadata to find the "
            "conda package name."
        )

    name = decode_pkg_from_oci(name)
    ver, build = tag.rsplit("-", maxsplit=2)
    ver = decode_version_build_from_oci(ver)
    build = decode_version_build_from_oci(build)

    if channel is not None and subdir is not None:
        prefix = f"{channel}/{subdir}/"
    else:
        prefix = ""

    return prefix + f"{name}-{ver}-{build}"
