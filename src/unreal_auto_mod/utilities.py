import os
import shutil

from unreal_auto_mod import file_io, settings
from unreal_auto_mod.data_structures import CompressionType, get_enum_from_val
from unreal_auto_mod.programs import unreal_engine


def custom_get_game_dir():
    return unreal_engine.get_game_dir(settings.get_game_exe_path())


def custom_get_game_paks_dir() -> str:
    alt_game_dir = os.path.dirname(custom_get_game_dir())
    if settings.get_is_using_alt_dir_name():
        return os.path.join(
            alt_game_dir, settings.get_alt_packing_dir_name(), "Content", "Paks"
        )
    return unreal_engine.get_game_paks_dir(
        settings.get_uproject_file(), custom_get_game_dir()
    )


def get_uproject_dir():
    return os.path.dirname(settings.get_uproject_file())


def get_uproject_unreal_auto_mod_dir():
    return f"{get_uproject_dir()}/Plugins/UnrealAutoMod"


def get_uproject_unreal_auto_mod_resources_dir():
    return f"{get_uproject_unreal_auto_mod_dir()}/Resources"


def get_use_mod_name_dir_name_override(mod_name: str) -> bool:
    return get_mods_info_dict_from_mod_name(mod_name)["use_mod_name_dir_name_override"]


def get_mod_name_dir_name_override(mod_name: str) -> str:
    return get_mods_info_dict_from_mod_name(mod_name)["mod_name_dir_name_override"]


def get_mod_name_dir_name(mod_name: str) -> str:
    if get_use_mod_name_dir_name_override(mod_name):
        return get_mod_name_dir_name_override(mod_name)
    return mod_name


def get_pak_dir_structure(mod_name: str) -> str:
    for info in settings.get_mods_info_list_from_json():
        if info["mod_name"] == mod_name:
            return info["pak_dir_structure"]
    pak_dir_structure_missing_error = "Could not find the proper pak dir structure within the mod entry in the provided settings file"
    raise RuntimeError(pak_dir_structure_missing_error)


def get_mod_compression_type(mod_name: str) -> CompressionType:
    for info in settings.get_mods_info_list_from_json():
        if info["mod_name"] == mod_name:
            compression_str = info["compression_type"]
            return CompressionType(get_enum_from_val(CompressionType, compression_str))
    missing_compression_type_error = (
        f'Could not find the compression type for the following mod name "{mod_name}"'
    )
    raise RuntimeError(missing_compression_type_error)


def get_unreal_mod_tree_type_str(mod_name: str) -> str:
    for info in settings.get_mods_info_list_from_json():
        if info["mod_name"] == mod_name:
            return info["mod_name_dir_type"]
    missing_mod_tree_type_error = f'Was unable to find the unreal mod tree type for the following mod name "{mod_name}"'
    raise RuntimeError(missing_mod_tree_type_error)


def get_mods_info_dict_from_mod_name(mod_name: str) -> dict:
    for info in settings.get_mods_info_list_from_json():
        if info["mod_name"] == mod_name:
            return dict(info)
    missing_mods_info_dict_error = (
        f'Was unable to find the mods info dict for the following mod name "{mod_name}"'
    )
    raise RuntimeError(missing_mods_info_dict_error)


def is_mod_name_in_list(mod_name: str) -> bool:
    return any(
        info["mod_name"] == mod_name for info in settings.get_mods_info_list_from_json()
    )


def get_mod_name_dir(mod_name: str) -> str:
    if is_mod_name_in_list(mod_name):
        return f"{unreal_engine.get_uproject_dir(settings.get_uproject_file())}/Saved/Cooked/{get_unreal_mod_tree_type_str(mod_name)}/{mod_name}"
    get_mod_name_dir_name_error = "Was unable to find the mod name dir name"
    raise RuntimeError(get_mod_name_dir_name_error)


def get_mod_name_dir_files(mod_name: str) -> list:
    return file_io.get_files_in_tree(get_mod_name_dir(mod_name))


def get_persistent_mod_files(mod_name: str) -> list:
    return file_io.get_files_in_tree(settings.get_persistent_mod_dir(mod_name))


def clean_working_dir():
    working_dir = settings.get_working_dir()
    if os.path.isdir(working_dir):
        shutil.rmtree(working_dir)


def filter_file_paths(paths_dict: dict) -> dict:
    filtered_dict = {}
    path_dict_keys = paths_dict.keys()
    for path_dict_key in path_dict_keys:
        if os.path.isfile(path_dict_key):
            filtered_dict[path_dict_key] = paths_dict[path_dict_key]
    return filtered_dict


def get_game_window_title() -> str:
    if settings.get_override_automatic_window_title_finding():
        return settings.get_window_title_override()
    return unreal_engine.get_game_process_name(settings.get_game_exe_path())
