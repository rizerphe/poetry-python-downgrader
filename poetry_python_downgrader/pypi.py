"""An interface to PyPI for fetching package information."""

from __future__ import annotations
import logging

import aiohttp
from poetry.core.constraints.version import Version, parse_constraint

logger = logging.getLogger(__name__)

PYPI_URL = "https://pypi.org/pypi"
TIMEOUT = 5


async def fetch_package_info(package: str, repository: str = PYPI_URL) -> dict | None:
    """Fetch package information from PyPI."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{repository}/{package}/json", timeout=TIMEOUT
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error("Failed to fetch package info for %s: %s", package, e)
            return None


def is_version_compatible(release_info: list[dict], target_python_version: str) -> bool:
    """Check if a release is compatible with the target Python version."""
    for info in release_info:
        requires_python = info.get("requires_python")
        if requires_python:
            specifier = parse_constraint(requires_python)
            if specifier.allows(Version.parse(target_python_version)):
                return True
    return False


def filter_compatible_versions(
    releases: dict[str, list[dict]], target_python_version: str
) -> list[str]:
    """Filter releases compatible with the target Python version."""
    return [
        release
        for release, release_info in releases.items()
        if is_version_compatible(release_info, target_python_version)
    ]


def filter_max_version(versions: list[str], max_version: Version | None) -> list[str]:
    """Filter versions that are less than or equal to the max version."""
    if max_version:
        return [v for v in versions if Version.parse(v) <= max_version]
    return versions


def parse_version(version: str) -> Version:
    """Parse a version string."""
    return Version.parse(version)


def get_highest_version(versions: list[str]) -> str | None:
    """Get the highest version from a list of version strings."""
    if not versions:
        return None
    return max(versions, key=parse_version)


async def get_compatible_versions(
    package: str,
    max_version: Version | None,
    target_python_version: str,
    repository: str = PYPI_URL,
) -> str | None:
    """Find the highest compatible version of a package for the target Python version."""
    package_info = await fetch_package_info(package, repository)
    if not package_info:
        return None

    releases = package_info["releases"]
    compatible_versions = filter_compatible_versions(releases, target_python_version)
    filtered_versions = filter_max_version(compatible_versions, max_version)
    return get_highest_version(filtered_versions)
