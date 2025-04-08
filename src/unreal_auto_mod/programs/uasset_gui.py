import os
import shutil

from unreal_auto_mod import file_io, utilities


def download_uasset_gui(output_directory: str):
    url = "https://github.com/atenfyr/UAssetGUI/releases/latest/download/UAssetGUI.exe"
    download_path = f"{output_directory}/UAssetGUI.exe"
    file_io.download_file(url, download_path)


def install_uasset_gui(output_directory: str):
    os.makedirs(output_directory, exist_ok=True)
    download_uasset_gui(output_directory)
    exe_path = f"{output_directory}/UAssetGUI.exe"
    shutil.move(exe_path, f"{output_directory}/UAssetGUI.exe")


def get_uasset_gui_path(output_directory: str) -> str:
    return f"{output_directory}/UAssetGUI.exe"


def does_uasset_gui_exist() -> bool:
    return os.path.isfile(
        f"{utilities.get_uproject_unreal_auto_mod_resources_dir()}/UAssetGUI/UAssetGUI.exe"
    )
