import os
import shutil

from unreal_auto_mod import file_io, settings


def download_kismet_analyzer(output_directory: str):
    url = "https://github.com/trumank/kismet-analyzer/releases/download/latest/kismet-analyzer-3d06645-win-x64.zip"
    download_path = f"{output_directory}/kismet-analyzer-3d06645-win-x64.zip"
    file_io.download_file(url, download_path)


def install_kismet_analyzer(output_directory: str):
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(settings.get_working_dir(), exist_ok=True)
    download_kismet_analyzer(settings.get_working_dir())
    zip_path = f"{settings.get_working_dir()}/kismet-analyzer-3d06645-win-x64.zip"
    file_io.unzip_zip(zip_path, output_directory)
    shutil.move(
        f"{output_directory}/kismet-analyzer-3d06645-win-x64/kismet-analyzer.exe",
        f"{output_directory}/kismet-analyzer.exe",
    )


def get_kismet_analyzer_path(output_directory: str) -> str:
    return f"{output_directory}/kismet-analyzer-3d06645-win-x64/kismet-analyzer.exe"


def does_kismet_analyzer_exist(output_directory: str) -> bool:
    return os.path.isfile(get_kismet_analyzer_path(output_directory))
