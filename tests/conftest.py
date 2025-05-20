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


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    rhino = config.getoption("--rhino")
    framework = config.getoption("--framework")
    terminalreporter.write_sep("=", f"rhino {rhino} - (dotnet {framework})")


@pytest.fixture(scope="session")
def rhino_version(request):
    return request.config.getoption("--rhino")

@pytest.fixture(scope="session")
def dotnet_framework(request):
    return request.config.getoption("--framework")