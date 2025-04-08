import os
import pathlib
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any
import json

from unreal_auto_mod import (
    file_io,
    logger,
    process_management,
    window_management,
)
from unreal_auto_mod.programs import unreal_engine


@dataclass
class SettingsInformation:
    settings: dict[str, Any]
    init_settings_done: bool
    settings_json_dir: str
    program_dir: str
    mod_names: list[str]
    settings_json: str


settings_information = SettingsInformation(
    settings={},
    init_settings_done=False,
    settings_json_dir="",
    program_dir="",
    mod_names=[],
    settings_json="",
)


def init_settings(settings_json_path: pathlib.Path):
    with open(settings_json_path, "r") as file:
        raw_settings = json.load(file)
    # raw_settings = Dynaconf(settings_files=[settings_json_path])
    # settings_information.settings = configs.DynamicSettings(raw_settings)
    settings_information.settings = raw_settings
    settings = settings_information.settings
    process_name = os.path.basename(settings["game_info"]["game_exe_path"])
    window_management.change_window_name(settings["general_info"]["window_title"])
    auto_close_game = settings["process_kill_events"]["auto_close_game"]
    is_process_running = process_management.is_process_running(process_name)
    if auto_close_game and is_process_running:
        taskkill_path = shutil.which("taskkill")

        if taskkill_path:
            subprocess.run([taskkill_path, "/F", "/IM", process_name], check=False)
        else:
            taskkill_exe_not_found_error = "taskkill.exe not found."
            raise FileNotFoundError(taskkill_exe_not_found_error)
    settings_information.init_settings_done = True
    settings_information.settings_json = str(settings_json_path)
    settings_information.settings_json_dir = os.path.dirname(
        settings_information.settings_json
    )


def load_settings(settings_json: str):
    logger.log_message(f"settings json: {settings_json}")
    if not settings_information.init_settings_done:
        init_settings(pathlib.Path(settings_json))


def get_unreal_engine_dir() -> str:
    ue_dir = settings_information.settings["engine_info"]["unreal_engine_dir"]
    file_io.check_path_exists(ue_dir)
    return ue_dir


def is_unreal_pak_packing_enum_in_use():
    is_in_use = False
    for entry in get_mods_info_list_from_json():
        if entry["packing_type"] == "unreal_pak":
            is_in_use = True
    return is_in_use


def is_engine_packing_enum_in_use():
    is_in_use = False
    for entry in get_mods_info_list_from_json():
        if entry["packing_type"] == "engine":
            is_in_use = True
    return is_in_use


def get_game_exe_path() -> str:
    return settings_information.settings["game_info"]["game_exe_path"]


def get_git_info_repo_path() -> str:
    return settings_information.settings["git_info"]["repo_path"]


def get_game_launcher_exe_path() -> str:
    return settings_information.settings["game_info"]["game_launcher_exe"]


def get_override_automatic_launcher_exe_finding() -> bool:
    return settings_information.settings["game_info"][
        "override_automatic_launcher_exe_finding"
    ]


def get_uproject_file() -> str:
    return settings_information.settings["engine_info"]["unreal_project_file"]


def get_unreal_engine_packaging_main_command() -> str:
    return settings_information.settings["engine_info"]["engine_packaging_command"]


def get_unreal_engine_cooking_main_command() -> str:
    return settings_information.settings["engine_info"]["engine_cooking_command"]


def get_unreal_engine_building_main_command() -> str:
    return settings_information.settings["engine_info"]["engine_building_command"]


def get_cleanup_repo_path() -> str:
    return settings_information.settings["git_info"]["repo_path"]


def get_window_title() -> str:
    return settings_information.settings["general_info"]["window_title"]


def get_window_title_override() -> str:
    return settings_information.settings["game_info"]["window_title_override"]


def get_override_automatic_window_title_finding() -> bool:
    return settings_information.settings["game_info"][
        "override_automatic_window_title_finding"
    ]


def get_is_overriding_automatic_version_finding() -> bool:
    return settings_information.settings["repak_info"][
        "override_automatic_version_finding"
    ]


def get_engine_building_args() -> list:
    return settings_information.settings["engine_info"]["engine_building_args"]


def get_engine_packaging_args() -> list:
    return settings_information.settings["engine_info"]["engine_packaging_args"]


def get_engine_cooking_args() -> list:
    return settings_information.settings["engine_info"]["engine_cooking_args"]


def get_window_management_events() -> dict:
    return settings_information.settings["window_management_events"]


def get_override_working_dir() -> str:
    return settings_information.settings["general_info"]["working_dir"]


def get_is_overriding_default_working_dir() -> bool:
    return settings_information.settings["general_info"]["override_default_working_dir"]


def get_persistent_mod_dir(mod_name: str) -> str:
    return f"{settings_information.settings_json_dir}/mod_packaging/persistent_files/{mod_name}"


def get_persistent_mods_dir() -> str:
    return f"{settings_information.settings_json_dir}/mod_packaging/persistent_files"


def get_override_automatic_version_finding() -> bool:
    return settings_information.settings["engine_info"][
        "override_automatic_version_finding"
    ]


def get_alt_packing_dir_name() -> str:
    return settings_information.settings["packaging_uproject_name"]["name"]


def get_is_using_alt_dir_name() -> bool:
    return settings_information.settings["packaging_uproject_name"]["use_override"]


def get_mods_info_list_from_json() -> list:
    return settings_information.settings["mods_info"]


def get_exec_events() -> list:
    return settings_information.settings["exec_events"]


def get_ide_path() -> str:
    return settings_information.settings["optionals"]["ide_path"]


def get_blender_path():
    return settings_information.settings["optionals"]["blender_path"]


def get_game_info_launch_type_enum_str_value() -> str:
    return settings_information.settings["game_info"]["launch_type"]


def get_game_id() -> int:
    return settings_information.settings["game_info"]["game_id"]


def get_game_launch_params() -> list:
    return settings_information.settings["game_info"]["launch_params"]


def get_engine_launch_args() -> list:
    return settings_information.settings["engine_info"]["engine_launch_args"]


def custom_get_unreal_engine_version(engine_path: str) -> str:
    if get_override_automatic_version_finding():
        unreal_engine_major_version = settings_information.settings["engine_info"][
            "unreal_engine_major_version"
        ]
        unreal_engine_minor_version = settings_information.settings["engine_info"][
            "unreal_engine_minor_version"
        ]
        return f"{unreal_engine_major_version}.{unreal_engine_minor_version}"
    return unreal_engine.get_unreal_engine_version(engine_path)


def get_working_dir() -> str:
    if get_is_overriding_default_working_dir():
        working_dir = get_override_working_dir()
    else:
        working_dir = os.path.join(file_io.SCRIPT_DIR, "working_dir")
    os.makedirs(working_dir, exist_ok=True)
    return working_dir


def is_loose_packing_enum_in_use():
    is_in_use = False
    for entry in get_mods_info_list_from_json():
        if entry["packing_type"] == "loose":
            is_in_use = True
    return is_in_use
