import os
import os.path as op
import pytest


@pytest.fixture(scope="session", autouse=True)
def one_time_setup():
    import sys

    sys.path.append(r"C:\Users\ein\gits\rhino.inside-cpython")


def get_framework_id(dotnet_framework):
    if dotnet_framework == 4:
        return "net48"
    return f"net{dotnet_framework}.0"


def get_system_path(rhino_version):
    if os.name == "nt":
        path = rf"C:\Program Files\Rhino {rhino_version}\System"
        if op.exists(path):
            return path

        path = rf"C:\Program Files\Rhino {rhino_version} WIP\System"
        if op.exists(path):
            return path

    raise Exception("Unsupported platform")


def test_load_auto(rhino_version):
    if rhino_version != "auto":
        pytest.skip("Skipped running auto loader when specific version is specified")

    import rhinoinside

    rhinoinside.load()

    import System  # type: ignore
    import Rhino  # type: ignore

    assert f"v{System.Environment.Version}".startswith("v4.")
    assert f"v{Rhino.RhinoApp.Version}".startswith("v7.")


def test_load_from_path(rhino_version, dotnet_framework):
    if rhino_version == "auto":
        pytest.skip("Skipped running auto loader when specific version is specified")

    rhino = get_system_path(rhino_version)
    dfwid = get_framework_id(dotnet_framework)
    print(f"Loading Rhino v{rhino_version} on dotnet {dfwid}")

    import rhinoinside

    rhinoinside.load(rhino, dfwid)

    import System  # type: ignore
    import Rhino  # type: ignore

    assert f"v{System.Environment.Version}".startswith(f"v{dotnet_framework}.")
    assert f"v{Rhino.RhinoApp.Version}".startswith(f"v{rhino_version}.")


def test_interpolated_curve_length():
    import System  # type: ignore
    import Rhino  # type: ignore

    # for now, you need to explicitly use floating point
    # numbers in Point3d constructor
    pts = System.Collections.Generic.List[Rhino.Geometry.Point3d]()
    pts.Add(Rhino.Geometry.Point3d(0.0, 0.0, 0.0))
    pts.Add(Rhino.Geometry.Point3d(1.0, 0.0, 0.0))
    pts.Add(Rhino.Geometry.Point3d(1.5, 2.0, 0.0))

    crv = Rhino.Geometry.Curve.CreateInterpolatedCurve(pts, 3)
    print(crv.GetLength())
