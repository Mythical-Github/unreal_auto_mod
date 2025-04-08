import os
import shutil

import requests

from unreal_auto_mod import file_io, logger


def get_latest_stove_version():
    api_url = "https://api.github.com/repos/bananaturtlesandwich/stove/releases/latest"
    try:
        # Attempt to fetch the latest release information
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Parse the JSON response
        latest_release = response.json()
        return latest_release.get(
            "tag_name"
        )  # Use .get() to avoid KeyError if 'tag_name' is missing

    except requests.exceptions.HTTPError as http_err:
        logger.log_message(f"HTTP error occurred while accessing {api_url}: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.log_message(
            f"Request error occurred while accessing {api_url}: {req_err}"
        )
    except ValueError as val_err:
        logger.log_message(f"JSON parsing error: {val_err}")  # Catches invalid JSON

    return None  # Return None in case of failure


def download_stove(output_directory: str):
    latest_version = get_latest_stove_version()
    if latest_version:
        url = f"https://github.com/bananaturtlesandwich/stove/releases/download/{latest_version}/stove.exe"
    else:
        url = "https://github.com/bananaturtlesandwich/stove/releases/download/0.13.1-alpha/stove.exe"

    download_path = f"{output_directory}/stove.exe"
    file_io.download_file(url, download_path)


def install_stove(output_directory: str):
    os.makedirs(output_directory, exist_ok=True)
    download_stove(output_directory)
    exe_path = f"{output_directory}/stove.exe"
    shutil.move(exe_path, f"{output_directory}/stove.exe")


def get_stove_path(output_directory: str) -> str:
    return f"{output_directory}/stove.exe"


def does_stove_exist(output_directory: str) -> bool:
    return os.path.isfile(get_stove_path(output_directory))
