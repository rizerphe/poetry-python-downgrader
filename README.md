# Poetry Python Downgrader

A tool to downgrade Poetry packages for compatibility with specific Python versions.

[![Build](https://github.com/rizerphe/poetry-python-downgrader/actions/workflows/build.yml/badge.svg)](https://github.com/rizerphe/poetry-python-downgrader/actions/workflows/build.yml) [![Coverage Status](https://coveralls.io/repos/github/rizerphe/poetry-python-downgrader/badge.svg?branch=main)](https://coveralls.io/github/rizerphe/poetry-python-downgrader?branch=main) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://badge.fury.io/py/poetry-python-downgrader.svg)](https://badge.fury.io/py/poetry-python-downgrader) [![As a github action](https://img.shields.io/badge/As_a_github_action-black?logo=GitHub%20Actions&logoColor=white)](https://github.com/rizerphe/poetry-python-downgrader-action)

This project is also available [as a GitHub Action](https://github.com/rizerphe/poetry-python-downgrader-action)!

## Quickstart

```sh
downgrade-pyproject-for-python pyproject.toml 3.8 --in-place
```

This command will modify your `pyproject.toml` file to make it compatible with Python 3.8. I would not recommend using the generated `pyproject.toml` file for anything but testing whether your project can be made compatible with a specific python version - this is in no way reliable enough to publish.

## Installation

**Using pipx (recommended)**

```sh
pipx install poetry-python-downgrader
```

## How it works

Poetry Python Downgrader analyzes your `pyproject.toml` file and performs the following steps:

-   Reads the current dependencies and their version constraints.
-   For each dependency, it queries PyPI to find the highest version compatible with the target Python version.
-   Updates the `pyproject.toml` file with the new version constraints.
-   Removes dependencies that don't have a compatible version for the target Python version.
-   Updates the Python version requirement in the `pyproject.toml` file.

## Usage examples

**Basic usage**

```sh
downgrade-pyproject-for-python pyproject.toml 3.8
```

This command will print the updated `pyproject.toml` content to stdout.

**Save to a new file**

```sh
downgrade-pyproject-for-python pyproject.toml 3.8 -o new_pyproject.toml
```

This will save the updated content to `new_pyproject.toml`.

**Modify the original file**

```sh
downgrade-pyproject-for-python pyproject.toml 3.8 --in-place
```

**Pin versions**

```sh
downgrade-pyproject-for-python pyproject.toml 3.8 --pin-versions
```

This will pin the versions to exact compatible versions instead of using caret ranges; as a result you'll have a guarantee of never having too new of a version installed, which is useful in CI.

**Use a Custom PyPI Repository**

```sh
downgrade-pyproject-for-python pyproject.toml 3.8 -r https://custom-pypi.example.com/pypi
```

This doesn't add the custom repository, but replaces pypi with it, so only dependencies available there will stay.

## Backstory

This project was born out of a specific need in a complex Python project. The project was being developed for Python 3.10 and consisted of multiple independent components targeting different platforms. The goal was to continuously determine which components would work with Python 3.8 without manually downgrading each dependency every time.

The challenge was that some dependencies had Python 3.10 as the minimum requirement, and some were only compatible with 3.8 up to a specific version, making it impossible to simply run the tests on Python 3.8. The solution was to create a tool that could automatically downgrade all dependencies to be Python 3.8-compatible, remove incompatible dependencies.

This is the result, providing an automated way to adjust `pyproject.toml` files for compatibility with earlier Python versions.

## Note on Using Poetry's Internal APIs

This project directly uses some of Poetry's internal APIs, which is generally not recommended for production use. While this approach works well for a small project like this, one that's not ever meant to be used in a production environment, be aware that future updates to Poetry might break compatibility. Use this tool with caution and feel free to open an issue if something breaks!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
