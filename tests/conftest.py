import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--rhino",
        action="store",
        default="7",
        help="Rhino version to run tests on"
    )
    parser.addoption(
        "--framework",
        action="store",
        default="4.8",
        help="dotnet framework to run tests on"
    )


@pytest.fixture(scope="session")
def rhino_version(request):
    return request.config.getoption("--rhino")

@pytest.fixture(scope="session")
def dotnet_framework(request):
    return request.config.getoption("--framework")