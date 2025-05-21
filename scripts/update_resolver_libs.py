#! python 3
#r: requests
#r: packaging

import re
import os.path as op
import zipfile
import requests
from pathlib import Path
from packaging.version import Version


def get_latest_nuget_version(package_name, version_pattern=None):
    """
    Fetches the latest version of a NuGet package, optionally filtered by a version pattern like '8.*'.

    Parameters:
        package_name (str): The NuGet package ID (case-insensitive).
        version_pattern (str, optional): e.g., '8.*', '9.*', or None for all versions.

    Returns:
        str: The latest matching version string.

    Raises:
        ValueError: If the package or matching versions are not found.
    """
    package_id = package_name.lower()
    url = f"https://api.nuget.org/v3-flatcontainer/{package_id}/index.json"

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Package '{package_name}' not found on NuGet.")

    versions = response.json().get("versions", [])

    if version_pattern:
        match = re.fullmatch(r"(\d+)\.\*", version_pattern)
        if not match:
            raise ValueError("version_pattern must be like '8.*', '9.*', etc.")
        major = int(match.group(1))
        versions = [v for v in versions if Version(v).major == major]

    if not versions:
        raise ValueError(f"No versions found for '{package_name}' matching '{version_pattern}'.")

    return str(max(versions, key=Version))


def download_nupkg(package_name, version, destination_folder: Path):
    """
    Downloads a .nupkg file from NuGet for the given package and version.

    Parameters:
        package_name (str): The NuGet package ID (case-insensitive).
        version (str): The exact version to download (e.g., '8.6.0').
        destination_folder (str or Path): Folder to save the downloaded .nupkg file.

    Returns:
        Path: The path to the downloaded .nupkg file.

    Raises:
        Exception: If the file could not be downloaded.
    """
    pkg = package_name.lower()
    ver = version.lower()
    url = f"https://api.nuget.org/v3-flatcontainer/{pkg}/{ver}/{pkg}.{ver}.nupkg"

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise Exception(f"Failed to download {package_name} {version}: HTTP {response.status_code}")

    file_path = destination_folder / f"{pkg}.{ver}.nupkg"

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return file_path


def extract_file_from_nupkg(nupkg_path, file_to_extract, output_path: Path):
    """
    Extracts a specific file from a .nupkg (zip) archive.

    Parameters:
        nupkg_path (str or Path): Path to the .nupkg file.
        file_to_extract (str): The internal path of the file to extract (e.g., 'lib/net48/RhinoInside.dll').
        output_path (str or Path): Path where the extracted file will be saved.

    Raises:
        FileNotFoundError: If the file_to_extract is not found in the archive.
    """
    nupkg_path = Path(nupkg_path)

    with zipfile.ZipFile(nupkg_path, 'r') as z:
        try:
            with z.open(file_to_extract) as source, open(output_path, 'wb') as target:
                target.write(source.read())
            print(f"Extracted '{file_to_extract}' to '{output_path}'")
        except KeyError:
            raise FileNotFoundError(f"File '{file_to_extract}' not found in {nupkg_path}")


def safe_delete_file(file_path):
    """
    Safely deletes a file if it exists and is a regular file.

    Parameters:
        file_path (str or Path): The path to the file to delete.

    Returns:
        bool: True if deleted, False if not found or not a file.
    """
    path = Path(file_path)
    try:
        if path.exists() and path.is_file():
            path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting {file_path}: {e}")
        return False


destination_folder = Path(op.dirname(op.dirname(__file__)), 'rhinoinside')
destination_folder.mkdir(parents=True, exist_ok=True)

v7 = get_latest_nuget_version("Rhino.Inside", "7.*")  # e.g., '7.0.0'
print(f'Embedding {v7}')
nupkg = download_nupkg("Rhino.Inside", v7, destination_folder)
extract_file_from_nupkg(nupkg, "lib/net48/RhinoInside.dll", destination_folder / "Rhino.Inside_v7_net48.dll")
safe_delete_file(nupkg)

v8 = get_latest_nuget_version("Rhino.Inside", "8.*")  # e.g., '8.0.7-beta'
print(f'Embedding {v8}')
nupkg = download_nupkg("Rhino.Inside", v8, destination_folder)
extract_file_from_nupkg(nupkg, "lib/net48/Rhino.Inside.dll", destination_folder / "Rhino.Inside_v8_net48.dll")
extract_file_from_nupkg(nupkg, "lib/net7.0/Rhino.Inside.dll", destination_folder / "Rhino.Inside_v8_net7.0.dll")
extract_file_from_nupkg(nupkg, "lib/net8.0/Rhino.Inside.dll", destination_folder / "Rhino.Inside_v8_net8.0.dll")
safe_delete_file(nupkg)

v9 = get_latest_nuget_version("Rhino.Inside", "9.*")  # e.g., '9.0.3-beta'
print(f'Embedding {v9}')
nupkg = download_nupkg("Rhino.Inside", v9, destination_folder)
extract_file_from_nupkg(nupkg, "lib/net48/Rhino.Inside.dll", destination_folder / "Rhino.Inside_v9_net48.dll")
extract_file_from_nupkg(nupkg, "lib/net9.0/Rhino.Inside.dll", destination_folder / "Rhino.Inside_v9_net9.0.dll")
safe_delete_file(nupkg)
