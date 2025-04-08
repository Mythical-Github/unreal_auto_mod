import os

from unreal_auto_mod import file_io, settings


def download_umodel():
    url = "https://github.com/Mythical-Github/UEViewer/releases/download/vStatic/umodel_win32.zip"
    download_path = f"{settings.get_working_dir()}/umodel_win32.zip"

    file_io.download_file(url, download_path)


def install_umodel(output_directory: str):
    download_umodel()
    os.makedirs(output_directory, exist_ok=True)
    zip_path = os.path.join(settings.get_working_dir(), "umodel_win32.zip")
    file_io.unzip_zip(zip_path, output_directory)


def get_umodel_path(output_directory: str) -> str:
    path = os.path.join(output_directory, "umodel_64.exe")
    return os.path.normpath(path)


def does_umodel_exist(output_directory: str) -> bool:
    return os.path.isfile(get_umodel_path(output_directory))
