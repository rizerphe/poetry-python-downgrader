"""Reads a pyproject.toml file."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

import click
import toml

if TYPE_CHECKING:
    from pathlib import Path


def read_toml(path: Path) -> dict[str, Any] | None:
    """Read a TOML file."""
    try:
        with path.open() as f:
            return toml.load(f)
    except toml.TomlDecodeError:
        click.echo(f"Failed to parse {path}. Ensure it's a valid TOML file.", err=True)
        return None
