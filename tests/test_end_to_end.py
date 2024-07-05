from click.testing import CliRunner
import pytest
import toml

from poetry_python_downgrader.cli import main


@pytest.fixture
def mock_pyproject(tmp_path):
    content = {
        "tool": {"poetry": {"dependencies": {"python": "^3.10", "numpy": "^2.0.0"}}}
    }
    pyproject_file = tmp_path / "pyproject.toml"
    with open(pyproject_file, "w") as f:
        toml.dump(content, f)
    return pyproject_file


def test_end_to_end(mock_pyproject):
    runner = CliRunner()
    result = runner.invoke(main, [str(mock_pyproject), "3.8", "--pin-versions", "-i"])
    assert result.exit_code == 0

    # Read the updated pyproject.toml
    with open(mock_pyproject, "r") as f:
        updated_content = toml.load(f)

    # Check if numpy was downgraded to 1.24.4
    assert updated_content["tool"]["poetry"]["dependencies"]["numpy"] == "1.24.4"
    assert updated_content["tool"]["poetry"]["dependencies"]["python"] == "^3.8"
