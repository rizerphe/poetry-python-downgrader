"""Downgrade packages to be compatible with a target Python version."""

import asyncio
import logging
from typing import Any, Awaitable

from poetry.core.constraints.version import Version, parse_constraint

from .pypi import get_compatible_versions

logger = logging.getLogger(__name__)


def get_constraint(constraint: Any) -> str:
    """Get the version constraint from a dependency."""
    return constraint if isinstance(constraint, str) else constraint["version"]


def min_version(constraint: str) -> Version | None:
    """Get the minimum version from a constraint."""
    c_object = parse_constraint(constraint)
    if hasattr(c_object, "allowed_min"):
        return c_object.allowed_min  # type: ignore
    return None


async def versions_for_all(
    packages: dict[str, Any],
    target_python_version: str,
    repository: str = "https://pypi.org/pypi",
) -> dict[str, tuple[str, str | None]]:
    """Get the compatible version of a package for a target Python version."""
    tasks: list[Awaitable[str | None]] = []
    package_names: list[str] = []
    original_constraints: list[str] = []

    for package, constraint in packages.items():
        if package == "python":
            continue

        version_constraint = get_constraint(constraint)

        tasks.append(
            get_compatible_versions(
                package,
                min_version(version_constraint),
                target_python_version,
                repository,
            )
        )
        package_names.append(package)
        original_constraints.append(version_constraint)

    results = await asyncio.gather(*tasks, return_exceptions=False)
    return dict(zip(package_names, zip(original_constraints, results)))


def set_version(
    dependencies: dict[str, str | dict[str, str]], package: str, version: str
) -> None:
    """Set the version of a package in the dependencies."""
    constraint = dependencies.get(package, "")
    if isinstance(constraint, str):
        dependencies[package] = version
    else:
        constraint["version"] = version


async def downgrade_packages(
    dependencies: dict[str, str | dict[str, str]],
    target_python_version: str,
    pin_version: bool = False,
    repository: str = "https://pypi.org/pypi",
) -> None:
    """Downgrade packages to be compatible with the target Python version."""
    for package, (original_version, compatible_version) in (
        await versions_for_all(dependencies, target_python_version, repository)
    ).items():
        if compatible_version is None:
            logger.info("Removing %s as no compatible version found", package)
            del dependencies[package]
            continue

        compatible_version = (
            compatible_version if pin_version else f"^{compatible_version}"
        )

        if original_version == compatible_version:
            logger.debug("Package %s is already compatible", package)
            continue

        logger.info(
            "Downgrading %s from %s to %s",
            package,
            original_version,
            compatible_version,
        )
        set_version(dependencies, package, compatible_version)

    dependencies["python"] = f"^{target_python_version}"
