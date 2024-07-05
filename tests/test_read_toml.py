from poetry_python_downgrader.read_toml import read_toml


def test_read_toml_valid(tmp_path):
    content = """
    [tool.poetry]
    name = "test-project"
    version = "0.1.0"
    """
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(content)
    result = read_toml(toml_file)
    assert result == {"tool": {"poetry": {"name": "test-project", "version": "0.1.0"}}}


def test_read_toml_invalid(tmp_path):
    content = """
    [tool.poetry
    name = "test-project"
    version = "0.1.0"
    """
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(content)
    result = read_toml(toml_file)
    assert result is None
