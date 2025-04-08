import json
import os

from unreal_auto_mod import file_io, process_management
from unreal_auto_mod.data_structures import PackagingDirType


def get_game_process_name(input_game_exe_path: str) -> str:
    return process_management.get_process_name(input_game_exe_path)


def get_unreal_engine_version(engine_path: str) -> str:
    version_file_path = f"{engine_path}/Engine/Build/Build.version"
    file_io.check_path_exists(version_file_path)
    with open(version_file_path) as f:
        version_info = json.load(f)
        unreal_engine_major_version = version_info.get("MajorVersion", 0)
        unreal_engine_minor_version = version_info.get("MinorVersion", 0)
        return f"{unreal_engine_major_version}.{unreal_engine_minor_version}"


def get_game_paks_dir(uproject_file_path: str, game_dir: str) -> str:
    return os.path.join(
        os.path.dirname(game_dir),
        get_uproject_name(uproject_file_path),
        "Content",
        "Paks",
    )


def get_is_game_iostore(uproject_file_path: str, game_dir: str) -> bool:
    extensions = ["ucas", "utoc"]
    _game_dir = game_dir
    _uproject_file_path = uproject_file_path
    is_game_iostore = False
    all_files = file_io.get_files_in_tree(
        get_game_paks_dir(_uproject_file_path, _game_dir)
    )
    for file in all_files:
        file_extensions = file_io.get_file_extensions(file)
        for file_extension in file_extensions:
            if file_extension in extensions:
                is_game_iostore = True
    return is_game_iostore


def get_game_dir(game_exe_path: str):
    return os.path.dirname(os.path.dirname(os.path.dirname(game_exe_path)))


def get_game_content_dir(game_dir: str):
    return os.path.join(game_dir, "Content")


def get_game_pak_folder_archives(uproject_file_path: str, game_dir: str) -> list:
    if get_is_game_iostore(uproject_file_path, game_dir):
        return ["pak", "utoc", "ucas"]
    return ["pak"]


def get_win_dir_type(unreal_engine_dir: str) -> PackagingDirType:
    if is_game_ue5(unreal_engine_dir):
        return PackagingDirType.WINDOWS
    return PackagingDirType.WINDOWS_NO_EDITOR


def get_editor_cmd_path(unreal_engine_dir: str) -> str:
    if get_win_dir_type(unreal_engine_dir) == PackagingDirType.WINDOWS_NO_EDITOR:
        engine_path_suffix = "UE4Editor-Cmd.exe"
    else:
        engine_path_suffix = "UnrealEditor-Cmd.exe"
    return f'"{unreal_engine_dir}/Engine/Binaries/Win64/{engine_path_suffix}"'


def is_game_ue5(unreal_engine_dir: str) -> bool:
    return get_unreal_engine_version(unreal_engine_dir).startswith("5")


def is_game_ue4(unreal_engine_dir: str) -> bool:
    return get_unreal_engine_version(unreal_engine_dir).startswith("4")


def get_unreal_editor_exe_path(unreal_engine_dir: str) -> str:
    if get_win_dir_type(unreal_engine_dir) == PackagingDirType.WINDOWS_NO_EDITOR:
        engine_path_suffix = "UE4Editor.exe"
    else:
        engine_path_suffix = "UnrealEditor.exe"
    return os.path.join(
        unreal_engine_dir, "Engine", "Binaries", "Win64", engine_path_suffix
    )


def get_win_dir_str(unreal_engine_dir: str) -> str:
    win_dir_type = "Windows"
    if is_game_ue4(unreal_engine_dir):
        win_dir_type = f"{win_dir_type}NoEditor"
    return win_dir_type


def get_cooked_uproject_dir(uproject_file_path: str, unreal_engine_dir: str) -> str:
    uproject_dir = get_uproject_dir(uproject_file_path)
    win_dir_name = get_win_dir_str(unreal_engine_dir)
    uproject_name = get_uproject_name(uproject_file_path)
    return os.path.join(uproject_dir, "Saved", "Cooked", win_dir_name, uproject_name)


def get_uproject_name(uproject_file_path: str) -> str:
    return os.path.splitext(os.path.basename(uproject_file_path))[0]


def get_uproject_dir(uproject_file_path: str) -> str:
    return os.path.dirname(uproject_file_path)


def get_saved_cooked_dir(uproject_file_path: str) -> str:
    uproject_dir = get_uproject_dir(uproject_file_path)
    return os.path.join(uproject_dir, "Saved", "Cooked")


def get_engine_window_title(uproject_file_path: str) -> str:
    return f"{process_management.get_process_name(uproject_file_path)[:-9]} - Unreal Editor"


def get_engine_process_name(unreal_dir: str) -> str:
    return process_management.get_process_name(get_unreal_editor_exe_path(unreal_dir))


def get_build_target_file_path(uproject_file_path: str) -> str:
    uproject_dir = get_uproject_dir(uproject_file_path)
    uproject_name = get_uproject_name(uproject_file_path)
    return os.path.join(uproject_dir, "Binaries", "Win64", f"{uproject_name}.target")


def has_build_target_been_built(uproject_file_path: str) -> bool:
    return os.path.exists(get_build_target_file_path(uproject_file_path))


def get_unreal_pak_exe_path(unreal_engine_dir: str) -> str:
    return os.path.join(
        unreal_engine_dir, "Engine", "Binaries", "Win64", "UnrealPak.exe"
    )


def get_game_window_title(input_game_exe_path: str) -> str:
    return os.path.splitext(get_game_process_name(input_game_exe_path))[0]


def get_new_uproject_json_contents(
    file_version: int = 3,
    engine_major_association: int = 4,
    engine_minor_association: int = 27,
    category: str = "Modding",
    description: str = "Uproject for modding, generated with unreal_auto_mod.",
) -> str:
    return f'''{{
  "FileVersion": "{file_version}",
  "EngineAssociation": "{engine_major_association}.{engine_minor_association}",
  "Category": "{category}",
  "Description": "{description}"
}}'''
