import os
import shutil

from unreal_auto_mod import file_io


def download_spaghetti(output_directory: str):
    url = "https://github.com/bananaturtlesandwich/spaghetti/releases/latest/download/spaghetti.exe"
    download_path = f"{output_directory}/spaghetti.exe"
    file_io.download_file(url, download_path)


def install_spaghetti(output_directory: str):
    os.makedirs(output_directory, exist_ok=True)
    download_spaghetti(output_directory)
    exe_path = f"{output_directory}/spaghetti.exe"
    shutil.move(exe_path, f"{output_directory}/spaghetti.exe")


def get_spaghetti_path(output_directory: str) -> str:
    return f"{output_directory}/spaghetti.exe"


def does_spaghetti_exist(output_directory: str) -> bool:
    return os.path.isfile(get_spaghetti_path(output_directory))
