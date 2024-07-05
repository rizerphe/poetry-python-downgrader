"""Command-line interface for poetry-python-downgrader."""

from __future__ import annotations
import asyncio
import logging
from pathlib import Path
import sys
from typing import Coroutine

import click
from poetry.core.constraints.version import Version, parse_constraint
import toml

from .downgrader import downgrade_packages
from .read_toml import read_toml

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# Version checking functions
def supports_version(constraint: str, version: str) -> bool:
    """Check if a version satisfies a constraint."""
    return parse_constraint(constraint).allows(Version.parse(version))


def supports_python_version(poetry_config: dict, target_python_version: str) -> bool:
    """Check if the target Python version is supported by the project."""
    python_version = poetry_config.get("dependencies", {}).get("python")
    return python_version is None or supports_version(
        python_version, target_python_version
    )


# Configuration extraction functions
def get_poetry_config(pyproject: dict) -> dict:
    """Extract poetry configuration from pyproject."""
    return pyproject.get("tool", {}).get("poetry", {})


def get_dependencies(poetry_config: dict) -> dict:
    """Get main dependencies from poetry configuration."""
    return poetry_config.get("dependencies", {})


def get_group_dependencies(poetry_config: dict) -> list[dict]:
    """Get dependencies from all groups in poetry configuration."""
    return [
        group.get("dependencies", {})
        for group in poetry_config.get("group", {}).values()
    ]


# Task creation and execution
def create_downgrade_tasks(
    dependencies: dict,
    group_dependencies: list[dict],
    target_python_version: str,
    pin_versions: bool,
    repository: str,
) -> list[Coroutine]:
    """Create downgrade tasks for main and group dependencies."""
    return [
        downgrade_packages(
            dependencies, target_python_version, pin_versions, repository
        )
    ] + [
        downgrade_packages(group, target_python_version, pin_versions, repository)
        for group in group_dependencies
    ]


async def run_tasks(tasks: list[Coroutine]) -> None:
    """Run a list of coroutines concurrently."""
    await asyncio.gather(*tasks)


# File operations
def write_output(
    pyproject: dict, output_path: Path, target_python_version: str
) -> None:
    """Write the updated pyproject to the output file."""
    try:
        with output_path.open("w") as f:
            toml.dump(pyproject, f)
        click.echo(
            f"Updated {output_path} for Python {target_python_version}", err=True
        )
    except IOError:
        click.echo(
            f"Failed to write to {output_path}. Check file permissions.", err=True
        )
        sys.exit(1)


def print_to_stdout(pyproject_path: Path) -> None:
    """Print the contents of the pyproject file to stdout."""
    with open(pyproject_path, "r", encoding="utf-8") as og_file:
        click.echo(og_file.read())


# Main logic
def process_pyproject(
    pyproject_path: Path,
    target_python_version: str,
    pin_versions: bool,
    repository: str,
) -> dict | None:
    """Process the pyproject file and return the updated config if needed."""
    pyproject = read_toml(pyproject_path)
    if pyproject is None:
        return None

    poetry_config = get_poetry_config(pyproject)

    if supports_python_version(poetry_config, target_python_version):
        click.echo(
            f"Python version {target_python_version} is already supported", err=True
        )
        return None

    dependencies = get_dependencies(poetry_config)
    group_dependencies = get_group_dependencies(poetry_config)

    downgrade_tasks = create_downgrade_tasks(
        dependencies,
        group_dependencies,
        target_python_version,
        pin_versions,
        repository,
    )
    asyncio.run(run_tasks(downgrade_tasks))

    return pyproject


# CLI command
@click.command()
@click.version_option()
@click.argument("pyproject_path", type=click.Path(exists=True, path_type=Path))
@click.argument("target_python_version")
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path; defaults to overwriting the input file",
    default=None,
)
@click.option(
    "-i",
    "--in-place",
    type=bool,
    help="Overwrite the input file",
    is_flag=True,
)
@click.option(
    "--pin-versions/--no-pin-versions",
    is_flag=True,
    help="Pin versions of packages to the exact compatible version",
)
@click.option(
    "-r",
    "--repository",
    type=str,
    help="Custom repository URL",
    default="https://pypi.org/pypi",
)
def main(  # pylint: disable=too-many-arguments
    pyproject_path: Path,
    target_python_version: str,
    output: Path | None,
    in_place: bool,
    pin_versions: bool,
    repository: str,
) -> None:
    """Downgrade packages in pyproject.toml to be compatible with a specific Python version."""
    if output is not None and in_place:
        raise click.UsageError("Cannot use both --output and --in-place")

    updated_pyproject = process_pyproject(
        pyproject_path, target_python_version, pin_versions, repository
    )

    if updated_pyproject is None:
        if output is None and not in_place:
            print_to_stdout(pyproject_path)
        return

    if output is None and in_place:
        output = pyproject_path

    if output is None:
        click.echo(toml.dumps(updated_pyproject))
    else:
        write_output(updated_pyproject, output, target_python_version)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
