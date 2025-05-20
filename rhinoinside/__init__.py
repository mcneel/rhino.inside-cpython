import re
import os
import os.path
import struct
import atexit
import signal
from typing import Union, TypeVar


RESOLVER_LIBNAME = "Rhino.Inside"


# create and hold onto an instance of RhinoCore to properly
# launch Rhino.Inside of python
__rhino_core = None


RhinoSystem = TypeVar("RhinoSystem", bound="_RhinoSystem")
Runtime = TypeVar("Runtime", bound="clr_loader.Runtime")  # type: ignore


class _DotNetFramework:
    def __init__(self, major: int, minor: int):
        self.major_version: int = major
        self.minor_version: int = minor
        self.is_netcore: bool = major != 48 and major >= 5
        self.identifier: str = f"net{major}.{minor}" if self.is_netcore else "net48"

    def __find_runtime_spec(self, runtimes) -> Runtime:
        version = f"{self.major_version}."
        name = (
            "Microsoft.WindowsDesktop.App"
            if os.name == "nt"
            else "Microsoft.NETCore.App"
        )
        candidates = [
            rt for rt in runtimes if rt.name == name and rt.version.startswith(version)
        ]
        candidates.sort(key=lambda spec: spec.version, reverse=True)
        if candidates:
            return candidates[0]

        raise RuntimeError(f"Failed to find {name} v{self.major_version}")

    def load(self) -> None:
        from pythonnet import load  # type: ignore

        if self.is_netcore:
            import clr_loader  # type: ignore

            runtime_spec = self.__find_runtime_spec(clr_loader.find_runtimes())
            runtime = clr_loader.get_coreclr(runtime_spec=runtime_spec)
            load(runtime)
        else:
            load()


class _RhinoSystem:
    @classmethod
    def get_major_version_from_dir(cls, rhino_dir: str) -> int:
        if rhino_dir:
            # determine installed rhino version by ready dotnet file version
            # of a shipped dotnet assembly. using NodeInCode since it is one
            # of the smallest assemblies
            dotnet_lib = os.path.join(rhino_dir, "NodeInCode.dll")
            if os.path.exists(dotnet_lib):
                import dnfile  # type: ignore

                dn = dnfile.dnPE(dotnet_lib, fast_load=True)
                dn.parse_data_directories()
                d = dn.net.mdtables.Assembly.rows[0]
                return d.MajorVersion
        return 7

    @classmethod
    def from_default(cls) -> RhinoSystem:
        return _RhinoSystem()

    @classmethod
    def from_version(cls, version: int = 7) -> RhinoSystem:
        c = cls()
        c.major_version = version
        # this can be none. resolver will figure out installed rhino
        # based on its own library version e.g. resolver v9 finds and loads Rhino v9
        c.system_path = None
        return c

    @classmethod
    def from_path(cls, system_path: str) -> RhinoSystem:
        c = cls()
        c.system_path = system_path
        # lets determine version since we need to know which resolver
        # library we need to load for this installed rhino
        c.major_version = _RhinoSystem.get_major_version_from_dir(system_path)
        return c

    def __init__(self):
        self.major_version: int = 7
        self.system_path: str = None

    def __get_libname(self, dotnet_framework: _DotNetFramework) -> str:
        return f"{RESOLVER_LIBNAME}_v{self.major_version}_{dotnet_framework.identifier}.dll"

    def __get_libfile(self, dotnet_framework: _DotNetFramework) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), self.__get_libname(dotnet_framework))

    def load(self, dotnet_framework: _DotNetFramework) -> None:
        # load netfx or netcore runtime first
        dotnet_framework.load()

        # determine which resolver library to load
        resolver = self.__get_libfile(dotnet_framework)

        # then load clr (this should return immediately since dotnet runtime is loaded already)
        import clr  # type: ignore

        clr.AddReference(resolver)

        # legacy resolver must be initialized first
        # and rhino dir explicitly set on the .RhinoSystemDirectory
        import RhinoInside  # type: ignore

        if dotnet_framework.is_netcore and self.system_path is not None:
            RhinoInside.Resolver.Initialize(str(self.system_path))

        # legacy version of resolver needed system path to be
        # manually set on the .RhinoSystemDirectory
        else:
            RhinoInside.Resolver.Initialize()
            if self.system_path is not None:
                RhinoInside.Resolver.RhinoSystemDirectory = self.system_path


# ensure core instance is disposed on exit
def __on_exit() -> None:
    global __rhino_core
    if (
        __rhino_core
        and hasattr(__rhino_core, "Dispose")
        and callable(__rhino_core.Dispose)
    ):
        __rhino_core.Dispose()
        __rhino_core = None


def __handle_terminate_signal(_1, _2) -> None:
    __on_exit()


def __parse_rhino_id(rhino_dir_or_version: str = None) -> _RhinoSystem:
    if isinstance(rhino_dir_or_version, str):
        if rhino_dir_or_version.isdigit():
            return _RhinoSystem.from_version(version=int(rhino_dir_or_version))
        else:
            return _RhinoSystem.from_path(system_path=rhino_dir_or_version)
    elif isinstance(rhino_dir_or_version, (int, float)):
        return _RhinoSystem.from_version(version=rhino_dir_or_version)

    return _RhinoSystem.from_default()


def __parse_framework_id(dotnet_framework_id: str) -> _DotNetFramework:
    m = re.search(r"net(?P<major>core|\d+)(\.(?P<minor>\d+))?", dotnet_framework_id)
    if m:
        major = m.group("major")
        major = int(major) if major and major.isdigit() else 5 if major == "core" else 0
        minor = m.group("minor")
        minor = int(minor) if minor and minor.isdigit() else 0
        return _DotNetFramework(major, minor or 0)

    raise Exception(f'Unknown dotnet framework identifier "{dotnet_framework_id}"')


def __assert_environ() -> None:
    if os.name != "nt":
        raise Exception("rhinoinside only works on Windows")

    bitness = 8 * struct.calcsize("P")
    if bitness != 64:
        raise Exception("rhinoinside only works in a 64 bit process")


def load(
    rhino_dir_or_major_version: Union[str, int] = 7, dotnet_framework_id: str = "net48"
) -> None:
    global __rhino_core
    if __rhino_core is None:
        if rhino_dir_or_major_version is None:
            raise ValueError("rhino_dir_or_major_version can not be None")

        if dotnet_framework_id is None:
            raise ValueError("dotnet_framework_id can not be None")

        __assert_environ()

        dotnet_framework = __parse_framework_id(dotnet_framework_id)
        rhino_system = __parse_rhino_id(rhino_dir_or_major_version)
        rhino_system.load(dotnet_framework)

        # now we can reference Rhino API and start rhino core
        import clr  # type: ignore

        clr.AddReference("RhinoCommon")
        import Rhino  # type: ignore

        __rhino_core = Rhino.Runtime.InProcess.RhinoCore()


def get_rhinocore():
    global __rhino_core
    if __rhino_core:
        return __rhino_core
    raise Exception("RhinoCore is not yet loaded or raised exception during load")


signal.signal(signal.SIGINT, __handle_terminate_signal)
signal.signal(signal.SIGTERM, __handle_terminate_signal)
atexit.register(__on_exit)
