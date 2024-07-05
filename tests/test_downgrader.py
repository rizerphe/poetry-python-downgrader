from unittest.mock import patch

import pytest

from poetry_python_downgrader.downgrader import (
    downgrade_packages,
    get_constraint,
    min_version,
    set_version,
    versions_for_all,
)


def test_get_constraint_string():
    assert get_constraint("^1.0.0") == "^1.0.0"


def test_get_constraint_dict():
    assert get_constraint({"version": "^1.0.0"}) == "^1.0.0"


def test_min_version():
    assert str(min_version("^1.2.3")) == "1.2.3"
    assert min_version("*") is None


@pytest.mark.asyncio
async def test_versions_for_all():
    packages = {
        "package1": "^1.0.0",
        "package2": {"version": "^2.0.0"},
        "python": "^3.8",
    }
    with patch(
        "poetry_python_downgrader.downgrader.get_compatible_versions"
    ) as mock_get_compatible_versions:
        mock_get_compatible_versions.side_effect = ["1.0.1", "2.0.1"]
        result = await versions_for_all(packages, "3.8")
    assert result == {"package1": ("^1.0.0", "1.0.1"), "package2": ("^2.0.0", "2.0.1")}


def test_set_version_string():
    dependencies = {"package": "^1.0.0"}
    set_version(dependencies, "package", "^1.1.0")
    assert dependencies["package"] == "^1.1.0"


def test_set_version_dict():
    dependencies = {"package": {"version": "^1.0.0"}}
    set_version(dependencies, "package", "^1.1.0")
    assert dependencies["package"]["version"] == "^1.1.0"


@pytest.mark.asyncio
async def test_downgrade_packages():
    dependencies = {"package1": "^1.0.0", "package2": "^2.0.0", "python": "^3.9"}
    with patch(
        "poetry_python_downgrader.downgrader.versions_for_all"
    ) as mock_versions_for_all:
        mock_versions_for_all.return_value = {
            "package1": ("^1.0.0", "1.0.1"),
            "package2": ("^2.0.0", None),
        }
        await downgrade_packages(dependencies, "3.8")
    assert dependencies == {"package1": "^1.0.1", "python": "^3.8"}


@pytest.mark.asyncio
async def test_downgrade_packages_pin_version():
    dependencies = {"package1": "^1.0.0", "python": "^3.9"}
    with patch(
        "poetry_python_downgrader.downgrader.versions_for_all"
    ) as mock_versions_for_all:
        mock_versions_for_all.return_value = {
            "package1": ("^1.0.0", "1.0.1"),
        }
        await downgrade_packages(dependencies, "3.8", pin_version=True)
    assert dependencies == {"package1": "1.0.1", "python": "^3.8"}
