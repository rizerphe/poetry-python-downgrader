from aiohttp import web
from poetry.core.constraints.version import Version
import pytest

from poetry_python_downgrader.pypi import (
    filter_compatible_versions,
    filter_max_version,
    get_compatible_versions,
    get_highest_version,
    is_version_compatible,
    parse_version,
)


async def mock_package_info(request):
    return web.json_response(
        {
            "info": {"version": "1.0.0"},
            "releases": {
                "1.0.0": [{"requires_python": ">=3.6"}],
                "1.1.0": [{"requires_python": ">=3.8"}],
                "2.0.0": [{"requires_python": ">=3.8"}],
            },
        }
    )


@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()
    app.router.add_get("/pypi/package/json", mock_package_info)

    return loop.run_until_complete(aiohttp_client(app))


def test_is_version_compatible():
    release_info = [{"requires_python": ">=3.6"}, {"requires_python": ">=3.8"}]
    assert is_version_compatible(release_info, "3.8")
    assert is_version_compatible(release_info, "3.7")
    assert not is_version_compatible(release_info, "3.4")


def test_filter_compatible_versions():
    releases = {
        "1.0.0": [{"requires_python": ">=3.6"}],
        "2.0.0": [{"requires_python": ">=3.8"}],
    }
    assert filter_compatible_versions(releases, "3.8") == ["1.0.0", "2.0.0"]
    assert filter_compatible_versions(releases, "3.7") == ["1.0.0"]


def test_filter_max_version():
    versions = ["1.0.0", "1.1.0", "2.0.0"]
    max_version = Version.parse("1.1.0")
    assert filter_max_version(versions, max_version) == ["1.0.0", "1.1.0"]


def test_parse_version():
    assert parse_version("1.2.3") == Version.parse("1.2.3")


def test_get_highest_version():
    versions = ["1.0.0", "1.1.0", "2.0.0"]
    assert get_highest_version(versions) == "2.0.0"


@pytest.mark.asyncio
async def test_get_compatible_versions(cli):
    result = await get_compatible_versions(
        "package", Version.parse("1.1.0"), "3.8", cli.make_url("/pypi")
    )
    assert result == "1.1.0"
    result = await get_compatible_versions(
        "package", Version.parse("1.1.0"), "3.7", cli.make_url("/pypi")
    )
    assert result == "1.0.0"
