import os

from unreal_auto_mod import file_io, settings


def get_fmodel_path(output_directory: str) -> str:
    return os.path.join(output_directory, "Fmodel.exe")


def install_fmodel(output_directory: str):
    download_fmodel()
    zip_path = os.path.join(settings.get_working_dir(), "Fmodel.zip")
    file_io.unzip_zip(zip_path, output_directory)


def download_fmodel():
    url = "https://github.com/4sval/FModel/releases/latest/download/FModel.zip"
    download_path = os.path.join(settings.get_working_dir(), "Fmodel.zip")
    file_io.download_file(url, download_path)


def does_fmodel_exist(output_directory: str) -> bool:
    return os.path.isfile(get_fmodel_path(output_directory))
