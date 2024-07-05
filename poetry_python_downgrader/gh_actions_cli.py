"""Github actions entrypoint for the CLI."""

from __future__ import annotations
import logging
from pathlib import Path

import click

from .cli import process_pyproject, write_output

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


@click.command()
@click.argument("pyproject_path", type=click.Path(exists=True, path_type=Path))
@click.argument("target_python_version")
@click.argument(
    "pin_versions",
    type=bool,
    default=False,
)
@click.argument(
    "repository",
    type=str,
    default="https://pypi.org/pypi",
)
def main(
    pyproject_path: Path,
    target_python_version: str,
    pin_versions: bool,
    repository: str,
) -> None:
    """Run downgrader in a Github Actions environment."""

    # target_python_version might be more than just a version number - e.g. pypy3.10
    # We need to extract the version number from it
    if target_python_version.startswith("pypy"):
        target_python_version = target_python_version[4:]

    # Now, we check whether the python version is valid, and return an error if it is not
    if not target_python_version.startswith("3."):
        click.echo(f"Unsupported Python version: {target_python_version}", err=True)
        raise click.Abort()  # Oh hey that's the third secret way to exit from a script

    updated_pyproject = process_pyproject(
        pyproject_path, target_python_version, pin_versions, repository
    )

    if updated_pyproject is None:
        return

    write_output(updated_pyproject, pyproject_path, target_python_version)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
