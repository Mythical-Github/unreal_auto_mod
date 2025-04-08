import json
import os
import shutil
import subprocess
import sys

from unreal_auto_mod import (
    app_runner,
    data_structures,
    engine,
    file_io,
    game_runner,
    hook_states,
    log_info,
    logger,
    packing,
    process_management,
    settings,
    utilities,
)
from unreal_auto_mod.programs import (
    fmodel,
    kismet_analyzer,
    spaghetti,
    uasset_gui,
    umodel,
    unreal_engine,
)
from unreal_auto_mod.threads import constant, game_monitor


@hook_states.hook_state_decorator(
    start_hook_state_type=data_structures.HookStateType.INIT
)
def init_thread_system():
    constant.constant_thread()


def close_thread_system():
    constant.stop_constant_thread()


# all things below this should be functions that correspond to cli logic


def generate_mods_other(*, use_symlinks: bool):
    packing.cooking()
    packing.generate_mods(use_symlinks=use_symlinks)
    game_runner.run_game()
    game_monitor.game_monitor_thread()


def test_mods(*, input_mod_names: list[str], toggle_engine: bool, use_symlinks: bool):
    if toggle_engine:
        engine.toggle_engine_off()
    for mod_name in input_mod_names:
        settings.settings_information.mod_names.append(mod_name)
    generate_mods_other(use_symlinks=use_symlinks)
    if toggle_engine:
        engine.toggle_engine_on()


def test_mods_all(*, toggle_engine: bool, use_symlinks: bool):
    if toggle_engine:
        engine.toggle_engine_off()
    for entry in settings.settings_information.settings["mods_info"]:
        settings.settings_information.mod_names.append(entry["mod_name"])
    generate_mods_other(use_symlinks=use_symlinks)
    if toggle_engine:
        engine.toggle_engine_on()


def full_run(
    *,
    input_mod_names: list[str],
    toggle_engine: bool,
    base_files_directory: str,
    output_directory: str,
    use_symlinks: bool,
):
    if toggle_engine:
        engine.toggle_engine_off()
    for mod_name in input_mod_names:
        settings.settings_information.mod_names.append(mod_name)
    packing.cooking()
    generate_mods(input_mod_names=input_mod_names, use_symlinks=use_symlinks)
    generate_mod_releases(
        mod_names=input_mod_names,
        base_files_directory=base_files_directory,
        output_directory=output_directory,
    )
    if toggle_engine:
        engine.toggle_engine_on()


def full_run_all(
    *,
    toggle_engine: bool,
    base_files_directory: str,
    output_directory: str,
    use_symlinks: bool,
):
    if toggle_engine:
        engine.toggle_engine_off()
    for entry in settings.settings_information.settings["mods_info"]:
        settings.settings_information.mod_names.append(entry["mod_name"])
    packing.cooking()
    generate_mods_all(use_symlinks=use_symlinks)
    generate_mod_releases_all(
        base_files_directory=base_files_directory, output_directory=output_directory
    )
    if toggle_engine:
        engine.toggle_engine_on()


def install_spaghetti(*, output_directory: str, run_after_install: bool):
    if not os.path.isfile(spaghetti.get_spaghetti_path(output_directory)):
        spaghetti.install_spaghetti(output_directory)
    if run_after_install:
        app_runner.run_app(spaghetti.get_spaghetti_path(output_directory))


def install_kismet_analyzer(*, output_directory: str, run_after_install: bool):
    # add shell stuff to run app later or something
    if not os.path.isfile(kismet_analyzer.get_kismet_analyzer_path(output_directory)):
        kismet_analyzer.install_kismet_analyzer(output_directory)
    if run_after_install:
        kismet_analyzer_path = kismet_analyzer.get_kismet_analyzer_path(
            output_directory
        )
        kismet_directory = os.path.dirname(kismet_analyzer_path)
        command = f'cd /d "{kismet_directory}" && "{kismet_analyzer_path}" -h && set ka=kismet-analyzer.exe && cmd /k'
        subprocess.run(command, check=False)


def install_uasset_gui(*, output_directory: str, run_after_install: bool):
    if not os.path.isfile(uasset_gui.get_uasset_gui_path(output_directory)):
        uasset_gui.install_uasset_gui(output_directory)
    else:
        logger.log_message(f'uasset_gui is already installed at: "{output_directory}"')
    if run_after_install:
        app_runner.run_app(uasset_gui.get_uasset_gui_path(output_directory))


def open_latest_log():
    log_prefix = log_info.LOG_INFO["log_name_prefix"]
    file_to_open = f"{file_io.SCRIPT_DIR}/logs/{log_prefix}latest.log"
    file_io.open_file_in_default(file_to_open)


def run_game(*, toggle_engine: bool):
    if toggle_engine:
        engine.toggle_engine_off()
    game_runner.run_game()
    game_monitor.game_monitor_thread()
    if toggle_engine:
        engine.toggle_engine_on()


def close_game():
    process_management.kill_process(os.path.basename(settings.get_game_exe_path()))


def run_engine():
    engine.open_game_engine()


def close_engine():
    engine.close_game_engine()


def install_umodel(*, output_directory: str, run_after_install: bool):
    if not umodel.does_umodel_exist(output_directory):
        umodel.install_umodel(output_directory)
    # Sets dir, so it's the dir opened by default in umodel
    # os.chdir(os.path.dirname(utilities.custom_get_game_dir()))
    if run_after_install:
        app_runner.run_app(umodel.get_umodel_path(output_directory))


def install_fmodel(*, output_directory: str, run_after_install: bool):
    if not os.path.isfile(fmodel.get_fmodel_path(output_directory)):
        fmodel.install_fmodel(output_directory)
    if run_after_install:
        app_runner.run_app(fmodel.get_fmodel_path(output_directory))


def get_solo_build_project_command() -> str:
    command = (
        f'"Engine\\Build\\BatchFiles\\RunUAT.{file_io.get_platform_wrapper_extension()}" {settings.get_unreal_engine_building_main_command()} '
        f'-project="{settings.get_uproject_file()}" '
    )
    for arg in settings.get_engine_building_args():
        command = f"{command} {arg}"
    return command


def run_proj_build_command(command: str):
    command_parts = command.split(" ")
    executable = command_parts[0]
    args = command_parts[1:]
    app_runner.run_app(
        exe_path=executable, args=args, working_dir=settings.get_unreal_engine_dir()
    )


def build(*, toggle_engine: bool):
    if toggle_engine:
        engine.toggle_engine_off()
    logger.log_message("Project Building Starting")
    run_proj_build_command(get_solo_build_project_command())
    logger.log_message("Project Building Complete")
    if toggle_engine:
        engine.toggle_engine_on()


def upload_changes_to_repo():
    repo_path = settings.settings_information.settings["git_info"]["repo_path"]
    branch = settings.settings_information.settings["git_info"]["repo_branch"]
    desc = input("Enter commit description: ")
    git_path = shutil.which("git")
    if git_path is None:
        raise FileNotFoundError(
            "Git executable not found. Ensure it's installed and in your system PATH."
        )

    status_result = subprocess.run(
        [git_path, "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=repo_path,
        check=False,
    )
    if status_result.returncode != 0 or not status_result.stdout.strip():
        logger.log_message("No changes detected or not in a Git repository.")
        sys.exit(1)

    checkout_result = subprocess.run(
        [git_path, "checkout", branch],
        capture_output=True,
        text=True,
        cwd=repo_path,
        check=False,
    )
    if checkout_result.returncode != 0:
        logger.log_message(f"Failed to switch to the {branch} branch.")
        sys.exit(1)

    subprocess.run([git_path, "add", "."], check=True, cwd=repo_path)

    commit_result = subprocess.run(
        [git_path, "commit", "-m", desc],
        capture_output=True,
        text=True,
        cwd=repo_path,
        check=False,
    )
    if commit_result.returncode != 0:
        logger.log_message("Commit failed.")
        sys.exit(1)

    push_result = subprocess.run(
        [git_path, "push", "origin", branch],
        capture_output=True,
        text=True,
        cwd=repo_path,
        check=False,
    )
    if push_result.returncode != 0:
        logger.log_message("Push failed.")
        sys.exit(1)

    logger.log_message("Changes committed and pushed successfully.")


def enable_mods(settings_json: str, mod_names: list):
    try:
        with open(settings_json, encoding="utf-8") as file:
            settings = json.load(file)

        mods_enabled = False

        for mod in settings.get("mods_info", []):
            if mod["mod_name"] in mod_names:
                if not mod["is_enabled"]:
                    mod["is_enabled"] = True
                    mods_enabled = True
                    logger.log_message(f"Mod '{mod['mod_name']}' has been enabled.")
                else:
                    logger.log_message(f"Mod '{mod['mod_name']}' is already enabled.")

        if mods_enabled:
            updated_json_str = json.dumps(
                settings, indent=4, ensure_ascii=False, separators=(",", ": ")
            )

            with open(settings_json, "w", encoding="utf-8") as file:
                file.write(updated_json_str)

            logger.log_message(f"Mods successfully enabled in '{settings_json}'.")
        else:
            logger.log_message(
                "No mods were enabled because all specified mods were already enabled."
            )

    except json.JSONDecodeError:
        logger.log_message(
            f"Error decoding JSON from file '{settings_json}'. Please check the file format."
        )


def disable_mods(settings_json: str, mod_names: list):
    try:
        with open(settings_json, encoding="utf-8") as file:
            settings = json.load(file)

        mods_disabled = False

        for mod in settings.get("mods_info", []):
            if mod["mod_name"] in mod_names:
                if mod["is_enabled"]:
                    mod["is_enabled"] = False
                    mods_disabled = True
                    logger.log_message(f"Mod '{mod['mod_name']}' has been disabled.")
                else:
                    logger.log_message(f"Mod '{mod['mod_name']}' is already disabled.")

        if mods_disabled:
            updated_json_str = json.dumps(
                settings, indent=4, ensure_ascii=False, separators=(",", ": ")
            )

            with open(settings_json, "w", encoding="utf-8") as file:
                file.write(updated_json_str)

            logger.log_message(f"Mods successfully disabled in '{settings_json}'.")
        else:
            logger.log_message(
                "No mods were disabled because all specified mods were already disabled."
            )

    except json.JSONDecodeError:
        logger.log_message(
            f"Error decoding JSON from file '{settings_json}'. Please check the file format."
        )


def add_mod(
    *,
    settings_json: str,
    mod_name: str,
    packing_type: str,
    pak_dir_structure: str,
    mod_name_dir_type: str,
    use_mod_name_dir_name_override: str,
    mod_name_dir_name_override: str,
    pak_chunk_num: int,
    compression_type: str,
    is_enabled: bool,
    asset_paths: list,
    tree_paths: list,
):
    try:
        with open(settings_json) as file:
            settings = json.load(file)

        new_mod = {
            "mod_name": mod_name,
            "pak_dir_structure": pak_dir_structure,
            "mod_name_dir_type": mod_name_dir_type,
            "use_mod_name_dir_name_override": use_mod_name_dir_name_override,
            "mod_name_dir_name_override": mod_name_dir_name_override,
            "pak_chunk_num": pak_chunk_num,
            "packing_type": packing_type,
            "compression_type": compression_type,
            "is_enabled": is_enabled,
            "file_includes": {"asset_paths": asset_paths, "tree_paths": tree_paths},
        }

        if "mods_info" not in settings:
            settings["mods_info"] = []

        existing_mod = next(
            (mod for mod in settings["mods_info"] if mod["mod_name"] == mod_name), None
        )
        if existing_mod:
            logger.log_message(f"Mod '{mod_name}' already exists. Updating its data.")
            settings["mods_info"].remove(existing_mod)

        settings["mods_info"].append(new_mod)

        settings = json.dumps(settings, indent=4)

        with open(settings_json, "w") as file:
            file.write(settings)

        logger.log_message(
            f"Mod '{mod_name}' successfully added/updated in '{settings_json}'."
        )
    except json.JSONDecodeError:
        logger.log_message(
            f"Error decoding JSON from file '{settings_json}'. Please check the file format."
        )


def remove_mods(settings_json: str, mod_names: list):
    try:
        with open(settings_json, encoding="utf-8") as file:
            settings = json.load(file)

        mods_removed = False

        mods_info = settings.get("mods_info", [])
        mods_info = [mod for mod in mods_info if mod["mod_name"] not in mod_names]

        if len(mods_info) < len(settings.get("mods_info", [])):
            mods_removed = True
            logger.log_message(f"Mods {', '.join(mod_names)} have been removed.")
        else:
            logger.log_message(
                "No mods were removed because none of the specified mods were found."
            )

        settings["mods_info"] = mods_info

        if mods_removed:
            updated_json_str = json.dumps(
                settings, indent=4, ensure_ascii=False, separators=(",", ": ")
            )

            with open(settings_json, "w", encoding="utf-8") as file:
                file.write(updated_json_str)

            logger.log_message(f"Mods successfully removed from '{settings_json}'.")

    except json.JSONDecodeError:
        logger.log_message(
            f"Error decoding JSON from file '{settings_json}'. Please check the file format."
        )


def get_solo_cook_project_command() -> str:
    command = (
        f'"Engine\\Build\\BatchFiles\\RunUAT.{file_io.get_platform_wrapper_extension()}" {settings.get_unreal_engine_cooking_main_command()} '
        f'-project="{settings.get_uproject_file()}" '
    )
    if not unreal_engine.has_build_target_been_built(settings.get_uproject_file()):
        build_arg = "-build"
        command = f"{command} {build_arg}"
    for arg in settings.get_engine_cooking_args():
        command = f"{command} {arg}"
    return command


def cook(*, toggle_engine: bool):
    if toggle_engine:
        engine.toggle_engine_off()
    logger.log_message("Content Cooking Starting")
    run_proj_build_command(get_solo_cook_project_command())
    logger.log_message("Content Cook Complete")
    if toggle_engine:
        engine.toggle_engine_on()


def get_solo_package_command() -> str:
    command = (
        f'"Engine\\Build\\BatchFiles\\RunUAT.{file_io.get_platform_wrapper_extension()}" {settings.get_unreal_engine_packaging_main_command()} '
        f'-project="{settings.get_uproject_file()}"'
    )
    # technically it shouldn't auto build itself, since this is not a auto run sequence but used in an explicit command
    # if not ue_dev_py_utils.has_build_target_been_built(utilities.get_uproject_file()):
    #     command = f'{command} -build'
    for arg in settings.get_engine_packaging_args():
        command = f"{command} {arg}"
    is_game_iostore = unreal_engine.get_is_game_iostore(
        settings.get_uproject_file(), utilities.custom_get_game_dir()
    )
    if is_game_iostore:
        command = f"{command} -iostore"
        logger.log_message("Check: Game is iostore")
    else:
        logger.log_message("Check: Game is not iostore")
    return command


def package(*, toggle_engine: bool, use_symlinks: bool):
    if toggle_engine:
        engine.toggle_engine_off()
    for entry in settings.get_mods_info_list_from_json():
        settings.settings_information.mod_names.append(entry["mod_name"])
    logger.log_message("Packaging Starting")
    run_proj_build_command(get_solo_package_command())
    packing.generate_mods(use_symlinks=use_symlinks)
    logger.log_message("Packaging Complete")
    if toggle_engine:
        engine.toggle_engine_on()


def resave_packages_and_fix_up_redirectors():
    engine.close_game_engine()
    arg = "-run=ResavePackages -fixupredirects"
    command = f'"{unreal_engine.get_unreal_editor_exe_path(settings.get_unreal_engine_dir())}" "{settings.get_uproject_file()}" {arg}'
    app_runner.run_app(command)


def cleanup_full():
    repo_path = settings.get_cleanup_repo_path()
    logger.log_message(f'Cleaning up repo at: "{repo_path}"')
    exe = "git"
    args = ["clean", "-d", "-X", "--force"]
    app_runner.run_app(
        exe_path=exe,
        exec_mode=data_structures.ExecutionMode.ASYNC,
        args=args,
        working_dir=repo_path,
    )
    logger.log_message(f'Cleaned up repo at: "{repo_path}"')

    dist_dir = f"{file_io.SCRIPT_DIR}/dist"
    if os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir)
    logger.log_message(f'Cleaned up dist dir at: "{dist_dir}"')

    working_dir = settings.get_working_dir()
    if os.path.isdir(working_dir):
        shutil.rmtree(working_dir)
    logger.log_message(f'Cleaned up working dir at: "{working_dir}"')


def cleanup_cooked():
    repo_path = settings.get_cleanup_repo_path()

    logger.log_message(
        f'Starting cleanup of Unreal Engine build directories in: "{repo_path}"'
    )

    build_dirs = ["Cooked"]

    for root, dirs, _ in os.walk(repo_path):
        for dir_name in dirs:
            if dir_name in build_dirs:
                full_path = os.path.normpath(os.path.join(root, dir_name))
                shutil.rmtree(full_path)
                logger.log_message(f"Removed directory: {full_path}")


def cleanup_build():
    repo_path = settings.get_cleanup_repo_path()

    logger.log_message(
        f'Starting cleanup of Unreal Engine build directories in: "{repo_path}"'
    )

    build_dirs = [
        "Intermediate",
        "DerivedDataCache",
        "Build",
        "Binaries",
    ]

    for root, dirs, _ in os.walk(repo_path):
        for dir_name in dirs:
            if dir_name in build_dirs:
                full_path = os.path.normpath(os.path.join(root, dir_name))
                shutil.rmtree(full_path)
                logger.log_message(f"Removed directory: {full_path}")


def cleanup_game():
    game_directory = os.path.dirname(utilities.custom_get_game_dir())
    file_list_json = os.path.join(
        settings.settings_information.settings_json_dir, "game_file_list.json"
    )
    delete_unlisted_files(game_directory, file_list_json)


def generate_game_file_list_json():
    game_directory = os.path.dirname(utilities.custom_get_game_dir())
    file_list_json = os.path.join(
        settings.settings_information.settings_json_dir, "game_file_list.json"
    )
    generate_file_paths_json(game_directory, file_list_json)


def cleanup_from_file_list(file_list: str, directory: str):
    delete_unlisted_files(directory, file_list)


def generate_file_list(directory: str, file_list: str):
    generate_file_paths_json(directory, file_list)


def generate_mods(*, input_mod_names: list[str], use_symlinks: bool):
    for mod_name in input_mod_names:
        settings.settings_information.mod_names.append(mod_name)
    for entry in settings.get_mods_info_list_from_json():
        settings.settings_information.mod_names.append(entry["mod_name"])
    packing.generate_mods(use_symlinks=use_symlinks)


def generate_mods_all(*, use_symlinks: bool):
    for entry in settings.get_mods_info_list_from_json():
        settings.settings_information.mod_names.append(entry["mod_name"])
        logger.log_message(entry["mod_name"])
    packing.generate_mods(use_symlinks=use_symlinks)


def make_unreal_pak_mod_release(
    singular_mod_info: dict, base_files_directory: str, output_directory: str
):
    mod_name = singular_mod_info["mod_name"]
    before_pak_file = f"{utilities.custom_get_game_paks_dir()}/{utilities.get_pak_dir_structure(mod_name)}/{mod_name}.pak"
    final_pak_file = f"{base_files_directory}/{mod_name}/{utilities.get_pak_dir_structure(mod_name)}/{mod_name}.pak"
    if os.path.isfile(final_pak_file):
        os.remove(final_pak_file)
    logger.log_message(os.path.dirname(final_pak_file))
    os.makedirs(os.path.dirname(final_pak_file), exist_ok=True)
    shutil.copyfile(before_pak_file, final_pak_file)
    file_io.zip_directory_tree(
        input_dir=f"{base_files_directory}/{mod_name}",
        output_dir=output_directory,
        zip_name=f"{mod_name}.zip",
    )


def make_repak_mod_release(
    singular_mod_info: dict, base_files_directory: str, output_directory: str
):
    mod_name = singular_mod_info["mod_name"]
    before_pak_file = f"{utilities.custom_get_game_paks_dir()}/{utilities.get_pak_dir_structure(mod_name)}/{mod_name}.pak"
    final_pak_file = f"{base_files_directory}/{mod_name}/{utilities.get_pak_dir_structure(mod_name)}/{mod_name}.pak"
    if os.path.isfile(final_pak_file):
        os.remove(final_pak_file)
    logger.log_message(os.path.dirname(final_pak_file))
    os.makedirs(os.path.dirname(final_pak_file), exist_ok=True)
    shutil.copyfile(before_pak_file, final_pak_file)
    file_io.zip_directory_tree(
        input_dir=f"{base_files_directory}/{mod_name}",
        output_dir=output_directory,
        zip_name=f"{mod_name}.zip",
    )


def make_engine_mod_release(
    singular_mod_info: dict, base_files_directory: str, output_directory: str
):
    mod_name = singular_mod_info["mod_name"]
    uproject_file = settings.get_uproject_file()
    mod_files = []
    pak_chunk_num = singular_mod_info["pak_chunk_num"]
    uproject_file = settings.get_uproject_file()
    uproject_dir = unreal_engine.get_uproject_dir(uproject_file)
    win_dir_str = unreal_engine.get_win_dir_str(settings.get_unreal_engine_dir())
    uproject_name = unreal_engine.get_uproject_name(uproject_file)
    prefix = f"{uproject_dir}/Saved/StagedBuilds/{win_dir_str}/{uproject_name}/Content/Paks/pakchunk{pak_chunk_num}-{win_dir_str}."
    mod_files.append(prefix)
    for file in mod_files:
        for suffix in unreal_engine.get_game_pak_folder_archives(
            uproject_file, utilities.custom_get_game_dir()
        ):
            dir_engine_mod = f"{utilities.custom_get_game_dir()}/Content/Paks/{utilities.get_pak_dir_structure(mod_name)}"
            os.makedirs(dir_engine_mod, exist_ok=True)
            before_file = f"{file}{suffix}"
            after_file = f"{base_files_directory}/{mod_name}/{utilities.get_pak_dir_structure(mod_name)}/{mod_name}.{suffix}"
            if os.path.isfile(after_file):
                os.remove(after_file)
            os.makedirs(os.path.dirname(after_file), exist_ok=True)
            shutil.copyfile(before_file, after_file)
    file_io.zip_directory_tree(
        input_dir=f"{base_files_directory}/{mod_name}",
        output_dir=output_directory,
        zip_name=f"{mod_name}.zip",
    )


def get_mod_files_asset_paths_for_loose_mods(
    mod_name: str, base_files_directory: str
) -> dict:
    file_dict = {}
    cooked_uproject_dir = unreal_engine.get_cooked_uproject_dir(
        settings.get_uproject_file(), settings.get_unreal_engine_dir()
    )
    mod_info = packing.get_mod_pak_entry(mod_name)
    for asset in mod_info["file_includes"]["asset_paths"]:
        base_path = f"{cooked_uproject_dir}/{asset}"
        for extension in file_io.get_file_extensions(base_path):
            before_path = f"{base_path}{extension}"
            after_path = (
                f"{base_files_directory}/{mod_name}/mod_files/{asset}{extension}"
            )
            file_dict[before_path] = after_path
    return file_dict


def get_mod_files_tree_paths_for_loose_mods(
    mod_name: str, base_files_directory: str
) -> dict:
    file_dict = {}
    cooked_uproject_dir = unreal_engine.get_cooked_uproject_dir(
        settings.get_uproject_file(), settings.get_unreal_engine_dir()
    )
    mod_info = packing.get_mod_pak_entry(mod_name)
    for tree in mod_info["file_includes"]["tree_paths"]:
        tree_path = f"{cooked_uproject_dir}/{tree}"
        for entry in file_io.get_files_in_tree(tree_path):
            if os.path.isfile(entry):
                base_entry = os.path.splitext(entry)[0]
                for extension in file_io.get_file_extensions_two(entry):
                    before_path = f"{base_entry}{extension}"
                    relative_path = os.path.relpath(base_entry, cooked_uproject_dir)
                    after_path = f"{base_files_directory}/{mod_name}/mod_files/{relative_path}{extension}"
                    file_dict[before_path] = after_path
    return file_dict


def get_mod_files_persistent_paths_for_loose_mods(
    mod_name: str, base_files_directory: str
) -> dict:
    file_dict = {}
    persistent_mod_dir = settings.get_persistent_mod_dir(mod_name)

    for root, _, files in os.walk(persistent_mod_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, persistent_mod_dir)
            after_path = f"{base_files_directory}/{mod_name}/mod_files/{relative_path}"
            file_dict[file_path] = after_path
    return file_dict


def get_mod_files_mod_name_dir_paths_for_loose_mods(
    mod_name: str, base_files_directory: str
) -> dict:
    file_dict = {}
    cooked_game_name_mod_dir = f"{unreal_engine.get_cooked_uproject_dir(settings.get_uproject_file(), settings.get_unreal_engine_dir())}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}"

    for file in file_io.get_files_in_tree(cooked_game_name_mod_dir):
        relative_file_path = os.path.relpath(file, cooked_game_name_mod_dir)
        before_path = os.path.abspath(file)
        after_path = f"{base_files_directory}/{mod_name}/mod_files/{relative_file_path}"
        file_dict[before_path] = after_path
    return file_dict


def get_mod_paths_for_loose_mods(mod_name: str, base_files_directory: str) -> dict:
    file_dict = {}
    file_dict.update(
        get_mod_files_asset_paths_for_loose_mods(mod_name, base_files_directory)
    )
    file_dict.update(
        get_mod_files_tree_paths_for_loose_mods(mod_name, base_files_directory)
    )
    file_dict.update(
        get_mod_files_persistent_paths_for_loose_mods(mod_name, base_files_directory)
    )
    file_dict.update(
        get_mod_files_mod_name_dir_paths_for_loose_mods(mod_name, base_files_directory)
    )

    return file_dict


def make_loose_mod_release(
    singular_mod_info: dict, base_files_directory: str, output_directory: str
):
    mod_name = singular_mod_info["mod_name"]
    mod_files = get_mod_paths_for_loose_mods(mod_name, base_files_directory)
    dict_keys = mod_files.keys()
    for key in dict_keys:
        before_file = key
        after_file = mod_files[key]
        os.makedirs(os.path.dirname(after_file), exist_ok=True)
        if os.path.exists(before_file):
            if os.path.islink(after_file):
                os.unlink(after_file)
            if os.path.isfile(after_file):
                os.remove(after_file)
        if os.path.isfile(before_file):
            shutil.copy(before_file, after_file)
    file_io.zip_directory_tree(
        input_dir=f"{base_files_directory}/{mod_name}",
        output_dir=output_directory,
        zip_name=f"{mod_name}.zip",
    )


def generate_mod_release(
    mod_name: str, base_files_directory: str, output_directory: str
):
    singular_mod_info = next(
        (
            mod_info
            for mod_info in settings.get_mods_info_list_from_json()
            if mod_info["mod_name"] == mod_name
        ),
    )
    if singular_mod_info["packing_type"] == "unreal_pak":
        make_unreal_pak_mod_release(
            singular_mod_info, base_files_directory, output_directory
        )
    elif singular_mod_info["packing_type"] == "repak":
        make_repak_mod_release(
            singular_mod_info, base_files_directory, output_directory
        )
    elif singular_mod_info["packing_type"] == "engine":
        make_engine_mod_release(
            singular_mod_info, base_files_directory, output_directory
        )
    elif singular_mod_info["packing_type"] == "loose":
        make_loose_mod_release(
            singular_mod_info, base_files_directory, output_directory
        )


def generate_mod_releases(
    mod_names: list[str], base_files_directory: str, output_directory: str
):
    for mod_name in mod_names:
        generate_mod_release(mod_name, base_files_directory, output_directory)


def generate_mod_releases_all(base_files_directory: str, output_directory: str):
    for entry in settings.get_mods_info_list_from_json():
        generate_mod_release(entry["mod_name"], base_files_directory, output_directory)


def resync_dir_with_repo():
    repo_path = settings.get_cleanup_repo_path()
    """
    Resyncs a directory tree with its repository by discarding local changes and cleaning untracked files.

    :param repo_path: The path to the root of the git repository.
    """
    repo_path = os.path.abspath(repo_path)

    if not os.path.isdir(repo_path):
        repo_not_exist_error = (
            f"The specified path '{repo_path}' does not exist or is not a directory."
        )
        raise FileNotFoundError(repo_not_exist_error)

    if not os.path.isdir(os.path.join(repo_path, ".git")):
        not_valid_git_repo_path = (
            f"The specified path '{repo_path}' is not a valid Git repository."
        )
        raise ValueError(not_valid_git_repo_path)

    exe = "git"

    args = ["clean", "-f", "-d", "-x"]
    app_runner.run_app(exe_path=exe, args=args, working_dir=repo_path)

    args = ["reset", "--hard"]
    app_runner.run_app(exe_path=exe, args=args, working_dir=repo_path)

    logger.log_message(f"Successfully resynchronized the repository at '{repo_path}'.")


def generate_uproject(
    *,
    project_file: str,
    file_version: int = 3,
    engine_major_association: int = 4,
    engine_minor_association: int = 27,
    category: str = "Modding",
    description: str = "Uproject for modding, generated with ",
    ignore_safety_checks: bool = False,
) -> str:
    project_dir = os.path.dirname(project_file)
    os.makedirs(project_dir, exist_ok=True)

    if not ignore_safety_checks:
        # Validate file version
        if file_version not in range(1, 4):
            invalid_file_version_error = (
                f"Invalid file version: {file_version}. Valid values are 1-3."
            )
            raise ValueError(invalid_file_version_error)

        # Validate EngineMajorAssociation
        if engine_major_association not in range(4, 6):  # Only 4-5 is valid
            invalid_major_engine_version_error = f"Invalid EngineMajorAssociation: {engine_major_association}. Valid value is 4-5."
            raise ValueError(invalid_major_engine_version_error)

        # Validate EngineMinorAssociation
        if engine_minor_association not in range(28):  # Valid range is 0-27
            invalid_minor_engine_version_error = f"Invalid EngineMinorAssociation: {engine_minor_association}. Valid range is 0-27."
            raise ValueError(invalid_minor_engine_version_error)

        # Ensure the directory is empty
        project_dir = os.path.dirname(os.path.abspath(project_file))
        if os.path.exists(project_dir) and os.listdir(project_dir):
            cannot_generate_in_non_empty_dir_error = f'The directory "{project_dir}" is not empty. Cannot generate project here.'
            raise FileExistsError(cannot_generate_in_non_empty_dir_error)

    # Generate the JSON content for the .uproject file
    json_content = unreal_engine.get_new_uproject_json_contents(
        file_version,
        engine_major_association,
        engine_minor_association,
        category,
        description,
    )

    # Write the .uproject file
    try:
        with open(project_file, "w") as f:
            f.write(json_content)
    except OSError as e:
        failed_to_write_project_file_error = (
            f"Failed to write to file '{project_file}': {e}"
        )
        raise OSError(failed_to_write_project_file_error)

    return f"Successfully generated '{project_file}'."


def add_module_to_descriptor(
    descriptor_file: str, module_name: str, host_type: str, loading_phase: str
):
    if not os.path.isfile(descriptor_file):
        descriptor_file_not_exist_error = (
            f"The file '{descriptor_file}' does not exist."
        )
        raise FileNotFoundError(descriptor_file_not_exist_error)

    try:
        with open(descriptor_file) as file:
            uproject_data = json.load(file)
    except json.JSONDecodeError as e:
        failed_to_parse_json_error = (
            f"Failed to parse JSON from '{descriptor_file}': {e}"
        )
        raise ValueError(failed_to_parse_json_error)

    module_entry = {
        "Name": module_name,
        "Type": host_type,
        "LoadingPhase": loading_phase,
    }

    if "Modules" not in uproject_data:
        uproject_data["Modules"] = []

    uproject_data["Modules"] = [
        module
        for module in uproject_data["Modules"]
        if module.get("Name") != module_name
    ] + [module_entry]

    updated_data = json.dumps(uproject_data, indent=4)
    try:
        with open(descriptor_file, "w") as file:
            file.write(updated_data)
    except OSError as e:
        failed_to_write_error = f"Failed to write to '{descriptor_file}': {e}"
        raise OSError(failed_to_write_error)


def add_plugin_to_descriptor(
    descriptor_file: str, plugin_name: str, *, is_enabled: bool
):
    if not os.path.isfile(descriptor_file):
        file_does_not_exist_error = f"The file '{descriptor_file}' does not exist."
        raise FileNotFoundError(file_does_not_exist_error)

    try:
        with open(descriptor_file) as file:
            uproject_data = json.load(file)
    except json.JSONDecodeError as e:
        failed_to_parse_json_error = (
            f"Failed to parse JSON from '{descriptor_file}': {e}"
        )
        raise ValueError(failed_to_parse_json_error)

    plugin_entry = {"Name": plugin_name, "Enabled": is_enabled}

    if "Plugins" not in uproject_data:
        uproject_data["Plugins"] = []

    uproject_data["Plugins"] = [
        plugin
        for plugin in uproject_data["Plugins"]
        if plugin.get("Name") != plugin_name
    ] + [plugin_entry]

    updated_data = json.dumps(uproject_data, indent=4)
    try:
        with open(descriptor_file, "w") as file:
            file.write(updated_data)
    except OSError as e:
        failed_to_write_to_descriptor_error = (
            f"Failed to write to '{descriptor_file}': {e}"
        )
        raise OSError(failed_to_write_to_descriptor_error)


def remove_modules_from_descriptor(descriptor_file: str, module_names: list):
    if not os.path.isfile(descriptor_file):
        descriptor_not_found_error = f"The file '{descriptor_file}' does not exist."
        raise FileNotFoundError(descriptor_not_found_error)

    with open(descriptor_file) as file:
        uproject_data = json.load(file)

    if "Modules" in uproject_data:
        uproject_data["Modules"] = [
            module
            for module in uproject_data["Modules"]
            if module["Name"] not in module_names
        ]

    merged_data = json.dumps(uproject_data, indent=4)

    with open(descriptor_file, "w") as file:
        file.write(merged_data)


def remove_plugins_from_descriptor(descriptor_file: str, plugin_names: list):
    if not os.path.isfile(descriptor_file):
        descriptor_not_found_error = f"The file '{descriptor_file}' does not exist."
        raise FileNotFoundError(descriptor_not_found_error)

    with open(descriptor_file) as file:
        uproject_data = json.load(file)

    if "Plugins" in uproject_data:
        uproject_data["Plugins"] = [
            plugin
            for plugin in uproject_data["Plugins"]
            if plugin["Name"] not in plugin_names
        ]

    merged_data = json.dumps(uproject_data, indent=4)

    with open(descriptor_file, "w") as file:
        file.write(merged_data)


def generate_uplugin(
    *,
    plugins_directory: str,
    plugin_name: str,
    can_contain_content: bool,
    is_installed: bool,
    is_hidden: bool,
    no_code: bool,
    category: str,
    created_by: str,
    created_by_url: str,
    description: str,
    docs_url: str,
    editor_custom_virtual_path: str,
    enabled_by_default: bool,
    engine_major_version: int,
    engine_minor_version: int,
    support_url: str,
    version: float,
    version_name: str,
):
    os.makedirs(plugins_directory, exist_ok=True)

    plugin_data = {
        "FileVersion": 3,
        "Version": version,
        "VersionName": version_name,
        "FriendlyName": plugin_name,
        "Description": description,
        "Category": category,
        "CreatedBy": created_by,
        "CreatedByURL": created_by_url,
        "DocsURL": docs_url,
        "MarketplaceURL": "",
        "SupportURL": support_url,
        "EngineVersion": f"{engine_major_version}.{engine_minor_version}",
        "EnabledByDefault": enabled_by_default,
        "CanContainContent": can_contain_content,
        "IsBetaVersion": False,
        "IsExperimentalVersion": False,
        "Installed": is_installed,
        "Hidden": is_hidden,
        "NoCode": no_code,
        "Modules": [],
        "Plugins": [],
    }

    if editor_custom_virtual_path:
        plugin_data["EditorCustomVirtualPath"] = editor_custom_virtual_path

    plugin_data_string = json.dumps(plugin_data, indent=4)

    plugin_file_path = os.path.join(
        plugins_directory, plugin_name, f"{plugin_name}.uplugin"
    )

    os.makedirs(os.path.dirname(plugin_file_path), exist_ok=True)

    with open(plugin_file_path, "w") as plugin_file:
        plugin_file.write(plugin_data_string)

    logger.log_message(
        f"Plugin '{plugin_name}' generated successfully at {plugin_file_path}."
    )


def remove_uplugins(uplugin_paths: list):
    for uplugin_path in uplugin_paths:
        uplugin_dir = os.path.dirname(uplugin_path)
        if os.path.isdir(uplugin_dir):
            shutil.rmtree(uplugin_dir)


def generate_file_paths_json(dir_path, output_json):
    all_file_paths = []

    for root, _, files in os.walk(dir_path):
        for file in files:
            full_path = os.path.join(root, file)
            all_file_paths.append(full_path)

    json_string = json.dumps(all_file_paths)
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as json_file:
        json_file.write(json_string)

    logger.log_message(f"JSON file with all file paths created at: {output_json}")


def delete_unlisted_files(dir_path, json_file):
    with open(json_file) as file:
        allowed_files = set(json.load(file))

    for root, _, files in os.walk(dir_path):
        for file in files:
            full_path = os.path.join(root, file)
            if full_path not in allowed_files:
                os.remove(full_path)
                logger.log_message(f"Deleted: {full_path}")

    logger.log_message("Cleanup complete. All unlisted files have been removed.")


def save_json_to_file(json_string, file_path):
    try:
        parsed_json = json.loads(json_string)

        with open(file_path, "w") as file:
            json.dump(parsed_json, file, indent=4)

        logger.log_message(f"JSON data successfully saved to {file_path}")
    except json.JSONDecodeError as e:
        logger.log_message(f"Invalid JSON string: {e}")
