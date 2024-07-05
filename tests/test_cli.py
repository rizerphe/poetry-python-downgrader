from unittest.mock import ANY, MagicMock, patch

from click.testing import CliRunner
import pytest

from poetry_python_downgrader.cli import main


@pytest.fixture
def mock_read_toml():
    with patch("poetry_python_downgrader.cli.read_toml") as mock:
        yield mock


@pytest.fixture
def mock_downgrade_packages():
    with patch("poetry_python_downgrader.cli.downgrade_packages") as mock:
        yield mock


def test_main_unsupported_version(mock_read_toml, mock_downgrade_packages):
    mock_read_toml.return_value = {
        "tool": {"poetry": {"dependencies": {"python": "^3.9"}}}
    }
    runner = CliRunner()
    result = runner.invoke(main, ["pyproject.toml", "3.8"])
    assert result.exit_code == 0
    mock_downgrade_packages.assert_called()


def test_main_supported_version(mock_read_toml):
    mock_read_toml.return_value = {
        "tool": {"poetry": {"dependencies": {"python": "^3.8"}}}
    }
    runner = CliRunner()
    result = runner.invoke(main, ["pyproject.toml", "3.8"])
    assert result.exit_code == 0
    assert "Python version 3.8 is already supported" in result.output


def test_main_invalid_input():
    runner = CliRunner()
    result = runner.invoke(main, ["nonexistent.toml", "3.8"])
    assert result.exit_code != 0


def test_main_output_option(mock_read_toml, mock_downgrade_packages, tmp_path):
    mock_read_toml.return_value = {
        "tool": {"poetry": {"dependencies": {"python": "^3.9"}}}
    }
    output_file = tmp_path / "output.toml"
    runner = CliRunner()
    result = runner.invoke(main, ["pyproject.toml", "3.8", "-o", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()


def test_main_in_place_option(mock_read_toml, mock_downgrade_packages, tmp_path):
    mock_read_toml.return_value = {
        "tool": {"poetry": {"dependencies": {"python": "^3.9"}}}
    }
    input_file = tmp_path / "pyproject.toml"
    input_file.touch()
    runner = CliRunner()
    result = runner.invoke(main, [str(input_file), "3.8", "-i"])
    assert result.exit_code == 0


def test_main_pin_versions_option(mock_read_toml, mock_downgrade_packages):
    mock_read_toml.return_value = {
        "tool": {"poetry": {"dependencies": {"python": "^3.9"}}}
    }
    runner = CliRunner()
    result = runner.invoke(main, ["pyproject.toml", "3.8", "--pin-versions"])
    assert result.exit_code == 0
    mock_downgrade_packages.assert_called_with(ANY, "3.8", True, ANY)


def test_main_no_pin_versions_option(mock_read_toml, mock_downgrade_packages):
    mock_read_toml.return_value = {
        "tool": {"poetry": {"dependencies": {"python": "^3.9"}}}
    }
    runner = CliRunner()
    result = runner.invoke(main, ["pyproject.toml", "3.8", "--no-pin-versions"])
    assert result.exit_code == 0
    mock_downgrade_packages.assert_called_with(ANY, "3.8", False, ANY)
