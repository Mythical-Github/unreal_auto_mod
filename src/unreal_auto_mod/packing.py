import os
import shutil
from dataclasses import dataclass

from rich.progress import Progress

from unreal_auto_mod import (
    app_runner,
    data_structures,
    file_io,
    hook_states,
    logger,
    settings,
    utilities,
)
from unreal_auto_mod.data_structures import (
    CompressionType,
    HookStateType,
    PackingType,
    get_enum_from_val,
)
from unreal_auto_mod.programs import repak, unreal_engine, unreal_pak


@dataclass
class QueueInformation:
    install_queue_types: list[PackingType]
    uninstall_queue_types: list[PackingType]


queue_information = QueueInformation(install_queue_types=[], uninstall_queue_types=[])


command_queue = []
has_populated_queue = False


def populate_queue():
    for mod_info in settings.get_mods_info_list_from_json():
        if (
            mod_info["is_enabled"]
            and mod_info["mod_name"] in settings.settings_information.mod_names
        ):
            install_queue_type = PackingType(
                get_enum_from_val(PackingType, mod_info["packing_type"])
            )
            if install_queue_type not in queue_information.install_queue_types:
                queue_information.install_queue_types.append(install_queue_type)
        if (
            not mod_info["is_enabled"]
            and mod_info["mod_name"] in settings.settings_information.mod_names
        ):
            uninstall_queue_type = PackingType(
                get_enum_from_val(PackingType, mod_info["packing_type"])
            )
            if uninstall_queue_type not in queue_information.uninstall_queue_types:
                queue_information.uninstall_queue_types.append(uninstall_queue_type)


def get_mod_packing_type(mod_name: str) -> PackingType:
    for mods_info in settings.get_mods_info_list_from_json():
        if mod_name == mods_info["mod_name"]:
            return PackingType(
                get_enum_from_val(PackingType, mods_info["packing_type"])
            )
    invalid_packing_type_error = "invalid packing type found in config file"
    raise RuntimeError(invalid_packing_type_error)


def get_is_mod_name_in_use(mod_name: str) -> bool:
    return any(
        mod_name == mod_info["mod_name"]
        for mod_info in settings.get_mods_info_list_from_json()
    )


def get_mod_pak_entry(mod_name: str) -> dict:
    for info in settings.get_mods_info_list_from_json():
        if info["mod_name"] == mod_name:
            return dict(info)
    return {}


def get_is_mod_installed(mod_name: str) -> bool:
    return any(
        info["mod_name"] == mod_name for info in settings.get_mods_info_list_from_json()
    )


def get_engine_pak_command() -> str:
    command = (
        f'"Engine\\Build\\BatchFiles\\RunUAT.{file_io.get_platform_wrapper_extension()}" {settings.get_unreal_engine_packaging_main_command()} '
        f'-project="{settings.get_uproject_file()}"'
    )
    if not unreal_engine.has_build_target_been_built(settings.get_uproject_file()):
        command = f"{command} -build"
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


def get_cook_project_command() -> str:
    command = (
        f'"Engine\\Build\\BatchFiles\\RunUAT.{file_io.get_platform_wrapper_extension()}" {settings.get_unreal_engine_cooking_main_command()} '
        f'-project="{settings.get_uproject_file()}" '
        f"-skipstage "
        f"-nodebuginfo"
    )
    if not unreal_engine.has_build_target_been_built(settings.get_uproject_file()):
        build_arg = "-build"
        command = f"{command} {build_arg}"
    for arg in settings.get_engine_cooking_args():
        command = f"{command} {arg}"
    return command


def cook_uproject():
    run_proj_command(get_cook_project_command())


def package_uproject_non_iostore():
    run_proj_command(get_engine_pak_command())


def run_proj_command(command: str):
    command_parts = command.split(" ")
    executable = command_parts[0]
    args = command_parts[1:]
    app_runner.run_app(
        exe_path=executable, args=args, working_dir=settings.get_unreal_engine_dir()
    )


def handle_uninstall_logic(packing_type: PackingType):
    for mod_info in settings.get_mods_info_list_from_json():
        if (
            not mod_info["is_enabled"]
            and mod_info["mod_name"] in settings.settings_information.mod_names
            and get_enum_from_val(PackingType, mod_info["packing_type"]) == packing_type
        ):
            uninstall_mod(packing_type, mod_info["mod_name"])


@hook_states.hook_state_decorator(
    start_hook_state_type=HookStateType.PRE_PAK_DIR_SETUP,
    end_hook_state_type=HookStateType.POST_PAK_DIR_SETUP,
)
def handle_install_logic(packing_type: PackingType, *, use_symlinks: bool):
    for mod_info in settings.get_mods_info_list_from_json():
        if (
            mod_info["is_enabled"]
            and mod_info["mod_name"] in settings.settings_information.mod_names
            and get_enum_from_val(PackingType, mod_info["packing_type"]) == packing_type
        ):
            install_mod(
                packing_type=packing_type,
                mod_name=mod_info["mod_name"],
                compression_type=CompressionType(
                    get_enum_from_val(CompressionType, mod_info["compression_type"])
                ),
                use_symlinks=use_symlinks,
            )


@hook_states.hook_state_decorator(
    start_hook_state_type=HookStateType.PRE_MODS_UNINSTALL,
    end_hook_state_type=HookStateType.POST_MODS_UNINSTALL,
)
def mods_uninstall():
    for uninstall_queue_type in queue_information.uninstall_queue_types:
        handle_uninstall_logic(uninstall_queue_type)


@hook_states.hook_state_decorator(
    start_hook_state_type=HookStateType.PRE_MODS_INSTALL,
    end_hook_state_type=HookStateType.POST_MODS_INSTALL,
)
def mods_install(*, use_symlinks: bool):
    for install_queue_type in queue_information.install_queue_types:
        handle_install_logic(install_queue_type, use_symlinks=use_symlinks)


def generate_mods(*, use_symlinks: bool):
    populate_queue()
    mods_uninstall()
    mods_install(use_symlinks=use_symlinks)
    for command in command_queue:
        app_runner.run_app(command)


def uninstall_loose_mod(mod_name: str):
    mod_files = get_mod_paths_for_loose_mods(mod_name)
    dict_keys = mod_files.keys()
    for key in dict_keys:
        file_to_remove = mod_files[key]
        if os.path.isfile(file_to_remove):
            os.remove(file_to_remove)
        if os.path.islink(file_to_remove):
            os.unlink(file_to_remove)

    for folder in {os.path.dirname(file) for file in mod_files.values()}:
        if os.path.exists(folder) and not os.listdir(folder):
            os.removedirs(folder)


def uninstall_pak_mod(mod_name: str):
    extensions = unreal_engine.get_game_pak_folder_archives(
        settings.get_uproject_file(), utilities.custom_get_game_dir()
    )
    if unreal_engine.is_game_ue5(settings.get_unreal_engine_dir()):
        extensions.extend(["ucas", "utoc"])
    for extension in extensions:
        base_path = os.path.join(
            utilities.custom_get_game_paks_dir(),
            utilities.get_pak_dir_structure(mod_name),
        )
        file_path = os.path.join(base_path, f"{mod_name}.{extension}")
        sig_path = os.path.join(base_path, f"{mod_name}.sig")
        if os.path.isfile(file_path):
            os.remove(file_path)
        if os.path.islink(file_path):
            os.unlink(file_path)
        if os.path.isfile(sig_path):
            os.remove(sig_path)
        if os.path.islink(sig_path):
            os.unlink(sig_path)


def uninstall_mod(packing_type: PackingType, mod_name: str):
    if packing_type == PackingType.LOOSE:
        uninstall_loose_mod(mod_name)
    elif packing_type in list(PackingType):
        uninstall_pak_mod(mod_name)


def install_mod_sig(mod_name: str, *, use_symlinks: bool):
    game_paks_dir = utilities.custom_get_game_paks_dir()
    pak_dir_str = utilities.get_pak_dir_structure(mod_name)
    sig_method_type = data_structures.get_enum_from_val(
        data_structures.SigMethodType,
        utilities.get_mods_info_dict_from_mod_name(mod_name).get(
            "sig_method_type", "none"
        ),
    )
    sig_location = os.path.normpath(f"{game_paks_dir}/{pak_dir_str}/{mod_name}.sig")
    os.makedirs(os.path.dirname(sig_location), exist_ok=True)
    if sig_method_type in data_structures.SigMethodType:
        if sig_method_type == data_structures.SigMethodType.COPY:
            sig_files = file_io.filter_by_extension(
                file_io.get_files_in_dir(game_paks_dir), ".sig"
            )
            if len(sig_files) < 1:
                no_sigs_found = ""
                raise RuntimeError(no_sigs_found)
            before_sig_file = os.path.normpath(f"{game_paks_dir}/{sig_files[0]}")
            if use_symlinks:
                os.symlink(before_sig_file, sig_location)
            else:
                shutil.copy(before_sig_file, sig_location)
        if sig_method_type == data_structures.SigMethodType.EMPTY:
            if use_symlinks:
                other_sig_location = os.path.normpath(
                    f"{settings.get_working_dir()}/sig_files/{mod_name}.sig"
                )
                os.makedirs(os.path.dirname(other_sig_location), exist_ok=True)
                with open(other_sig_location, "w"):
                    pass
                os.symlink(other_sig_location, sig_location)
            else:
                with open(sig_location, "w"):
                    pass
    else:
        logger.log_message(
            f"Error: You have provided an invalid sig method type in your mod entry for the {mod_name} mod."
        )
        logger.log_message("Error: Valid options are:")
        for enum in data_structures.get_enum_strings_from_enum(
            data_structures.SigMethodType
        ):
            logger.log_message(
                f"Error: {data_structures.get_enum_from_val(data_structures.SigMethodType, enum)}"
            )
        raise RuntimeError


def install_loose_mod(mod_name: str, *, use_symlinks: bool):
    mod_files = get_mod_paths_for_loose_mods(mod_name)
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
            if use_symlinks:
                os.symlink(before_file, after_file)
            else:
                shutil.copyfile(before_file, after_file)


def install_engine_mod(mod_name: str, *, use_symlinks: bool):
    mod_files = []
    pak_chunk_num = utilities.get_mods_info_dict_from_mod_name(mod_name)[
        "pak_chunk_num"
    ]
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
            if not os.path.isfile(before_file):
                error_message = "Error: The engine did not generate a pak and/or ucas/utoc for your specified chunk id, this indicates an engine, project, or settings.json configuration issue."
                logger.log_message(error_message)
                raise FileNotFoundError(error_message)
            after_file = f"{dir_engine_mod}/{mod_name}.{suffix}"
            if os.path.islink(after_file):
                os.unlink(after_file)
            if os.path.isfile(after_file):
                os.remove(after_file)
            install_mod_sig(mod_name, use_symlinks=use_symlinks)
            if use_symlinks:
                os.symlink(before_file, after_file)
            else:
                shutil.copyfile(before_file, after_file)


def make_pak_repak(*, mod_name: str, use_symlinks: bool):
    pak_dir = f"{utilities.custom_get_game_paks_dir()}/{utilities.get_pak_dir_structure(mod_name)}"
    os.makedirs(pak_dir, exist_ok=True)
    os.chdir(pak_dir)

    compression_type_str = utilities.get_mods_info_dict_from_mod_name(mod_name)[
        "compression_type"
    ]
    before_symlinked_dir = f"{settings.get_working_dir()}/{mod_name}"

    if not os.path.isdir(before_symlinked_dir) or not os.listdir(before_symlinked_dir):
        logger.log_message(f"Error: {before_symlinked_dir}")
        logger.log_message(
            "Error: does not exist or is empty, indicating a packaging and/or config issue"
        )
        raise FileNotFoundError

    intermediate_pak_dir = (
        f"{settings.get_working_dir()}/{utilities.get_pak_dir_structure(mod_name)}"
    )
    os.makedirs(intermediate_pak_dir, exist_ok=True)
    intermediate_pak_file = f"{intermediate_pak_dir}/{mod_name}.pak"

    final_pak_location = f"{pak_dir}/{mod_name}.pak"

    command = f'"{repak.get_repak_package_path()}" pack "{before_symlinked_dir}" "{intermediate_pak_file}"'
    if compression_type_str != "None":
        command = f"{command} --compression {compression_type_str} --version {repak.get_repak_pak_version_str()}"
    if os.path.islink(final_pak_location):
        os.unlink(final_pak_location)
    if os.path.isfile(final_pak_location):
        os.remove(final_pak_location)
    app_runner.run_app(command)
    install_mod_sig(mod_name, use_symlinks=use_symlinks)
    if use_symlinks:
        os.symlink(intermediate_pak_file, final_pak_location)
    else:
        shutil.copyfile(intermediate_pak_file, final_pak_location)


def install_repak_mod(mod_name: str, *, use_symlinks: bool):
    mod_files_dict = get_mod_file_paths_for_manually_made_pak_mods(mod_name)
    mod_files_dict = utilities.filter_file_paths(mod_files_dict)

    with Progress() as progress:
        task = progress.add_task(
            f"[green]Copying files for {mod_name} mod...", total=len(mod_files_dict)
        )

        for before_file, after_file in mod_files_dict.items():
            if os.path.exists(after_file):
                os.remove(after_file)
            if not os.path.isdir(os.path.dirname(after_file)):
                os.makedirs(os.path.dirname(after_file))
            if os.path.isfile(before_file):
                shutil.copy2(before_file, after_file)

            progress.update(task, advance=1)
    make_pak_repak(mod_name=mod_name, use_symlinks=use_symlinks)


def install_mod(
    *,
    packing_type: PackingType,
    mod_name: str,
    compression_type: CompressionType,
    use_symlinks: bool,
):
    if packing_type == PackingType.LOOSE:
        install_loose_mod(mod_name, use_symlinks=use_symlinks)
    elif packing_type == PackingType.ENGINE:
        install_engine_mod(mod_name, use_symlinks=use_symlinks)
    elif packing_type == PackingType.REPAK:
        install_repak_mod(mod_name, use_symlinks=use_symlinks)
    elif packing_type == PackingType.UNREAL_PAK:
        unreal_pak.install_unreal_pak_mod(
            mod_name, compression_type, use_symlinks=use_symlinks
        )
    else:
        logger.log_message(
            f'Error: You have provided an invalid packing_type for your "{mod_name}" mod entry in your settings json'
        )
        logger.log_message(
            f'Error: You provided "{utilities.get_mods_info_dict_from_mod_name(mod_name).get("packing_type", "none")}".'
        )
        logger.log_message("Error: Valid packing type options are:")
        for entry in PackingType:
            logger.log_message(f'Error: "{entry.value}"')
        invalid_packing_type_error = (
            "Invalid packing type, or no packing type, provided for mod entry"
        )
        raise RuntimeError(invalid_packing_type_error)


def package_project_iostore():
    if unreal_engine.is_game_ue4(settings.get_unreal_engine_dir()):
        package_project_iostore_ue4()
    else:
        package_project_iostore_ue5()


def package_project_iostore_ue4():
    main_exec = f'"{settings.get_unreal_engine_dir()}/Engine/Build/BatchFiles/RunUAT.{file_io.get_platform_wrapper_extension()}t"'
    uproject_path = settings.get_uproject_file()
    editor_cmd_exe_path = unreal_engine.get_editor_cmd_path(
        settings.get_unreal_engine_dir()
    )
    archive_directory = f"{settings.get_working_dir()}/iostore_packaging/output"
    target_platform = "Win64"
    client_config = "Development"
    args = [
        f'-ScriptsForProject="{uproject_path}"',
        "BuildCookRun",
        "-nocompileeditor",
        "-installed",
        "-nop4",
        f'-project="{uproject_path}"',
        "-cook",
        "-stage",
        "-archive",
        f'-archivedirectory="{archive_directory}"',
        "-package",
        f'-ue4exe="{editor_cmd_exe_path}"',
        "-ddc=InstalledDerivedDataBackendGraph",
        "-iostore",
        "-pak",
        "-iostore",
        "-prereqs",
        "-nodebuginfo",
        "-manifests",
        f"-targetplatform={target_platform}",
        f'-clientconfig="{client_config}"',
        "-utf8output",
    ]
    app_runner.run_app(
        exe_path=main_exec, args=args, working_dir=settings.get_unreal_engine_dir()
    )


def package_project_iostore_ue5():
    main_exec = f'"{settings.get_unreal_engine_dir()}/Engine/Build/BatchFiles/RunUAT.{file_io.get_platform_wrapper_extension()}"'
    uproject_path = settings.get_uproject_file()
    editor_cmd_exe_path = unreal_engine.get_editor_cmd_path(
        settings.get_unreal_engine_dir()
    )
    archive_directory = f"{settings.get_working_dir()}/iostore_packaging/output"
    target_platform = "Win64"
    client_config = "Development"
    args = [
        f'-ScriptsForProject="{uproject_path}"',
        "BuildCookRun",
        "-nocompileeditor",
        "-installed",
        "-nop4",
        f'-project="{uproject_path}"',
        "-cook",
        "-stage",
        "-archive",
        f'-archivedirectory="{archive_directory}"',
        "-package",
        f'-unrealexe="{editor_cmd_exe_path}"',
        "-ddc=InstalledDerivedDataBackendGraph",
        "-iostore",
        "-pak",
        "-iostore",
        "-prereqs",
        "-nodebuginfo",
        "-manifests",
        f"-targetplatform={target_platform}",
        f'-clientconfig="{client_config}"',
        "-utf8output",
    ]
    app_runner.run_app(
        exe_path=main_exec, args=args, working_dir=settings.get_unreal_engine_dir()
    )


# for if you are just repacking an ini for an iostore game and don't need a ucas or utoc for example
# actually implement this later on
def does_iostore_game_need_utoc_ucas() -> bool:
    # needs_more_than_pak = True
    # return needs_more_than_pak
    return True


@hook_states.hook_state_decorator(
    start_hook_state_type=HookStateType.PRE_COOKING,
    end_hook_state_type=HookStateType.POST_COOKING,
)
def cooking():
    populate_queue()
    if unreal_engine.get_is_game_iostore(
        settings.get_uproject_file(), utilities.custom_get_game_dir()
    ):
        if does_iostore_game_need_utoc_ucas():
            package_project_iostore()
        else:
            cook_uproject()
    elif PackingType.ENGINE in queue_information.install_queue_types:
        package_uproject_non_iostore()
    else:
        cook_uproject()


def get_mod_files_asset_paths_for_loose_mods(mod_name: str) -> dict:
    file_dict = {}
    cooked_uproject_dir = unreal_engine.get_cooked_uproject_dir(
        settings.get_uproject_file(), settings.get_unreal_engine_dir()
    )
    mod_info = get_mod_pak_entry(mod_name)
    for asset in mod_info["file_includes"]["asset_paths"]:
        base_path = f"{cooked_uproject_dir}/{asset}"
        for extension in file_io.get_file_extensions(base_path):
            before_path = f"{base_path}{extension}"
            after_path = f"{utilities.custom_get_game_dir()}/{asset}{extension}"
            file_dict[before_path] = after_path
    return file_dict


def get_mod_files_tree_paths_for_loose_mods(mod_name: str) -> dict:
    file_dict = {}
    cooked_uproject_dir = unreal_engine.get_cooked_uproject_dir(
        settings.get_uproject_file(), settings.get_unreal_engine_dir()
    )
    mod_info = get_mod_pak_entry(mod_name)
    for tree in mod_info["file_includes"]["tree_paths"]:
        tree_path = f"{cooked_uproject_dir}/{tree}"
        for entry in file_io.get_files_in_tree(tree_path):
            if os.path.isfile(entry):
                base_entry = os.path.splitext(entry)[0]
                for extension in file_io.get_file_extensions_two(entry):
                    before_path = f"{base_entry}{extension}"
                    relative_path = os.path.relpath(base_entry, cooked_uproject_dir)
                    after_path = (
                        f"{utilities.custom_get_game_dir()}/{relative_path}{extension}"
                    )
                    file_dict[before_path] = after_path
    return file_dict


def get_mod_files_persistent_paths_for_loose_mods(mod_name: str) -> dict:
    file_dict = {}
    persistent_mod_dir = settings.get_persistent_mod_dir(mod_name)

    for root, _, files in os.walk(persistent_mod_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, persistent_mod_dir)
            game_dir = utilities.custom_get_game_dir()
            game_dir_path = os.path.join(game_dir, relative_path)
            file_dict[file_path] = game_dir_path
    return file_dict


def get_mod_files_mod_name_dir_paths_for_loose_mods(mod_name: str) -> dict:
    file_dict = {}
    cooked_game_name_mod_dir = f"{unreal_engine.get_cooked_uproject_dir(settings.get_uproject_file(), settings.get_unreal_engine_dir())}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}"
    for file in file_io.get_files_in_tree(cooked_game_name_mod_dir):
        relative_file_path = os.path.relpath(file, cooked_game_name_mod_dir)
        before_path = f"{cooked_game_name_mod_dir}/{relative_file_path}"
        after_base = utilities.custom_get_game_dir()
        after_path = f"{after_base}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}/{relative_file_path}"
        file_dict[before_path] = after_path
    return file_dict


def get_mod_paths_for_loose_mods(mod_name: str) -> dict:
    file_dict = {}
    file_dict.update(get_mod_files_asset_paths_for_loose_mods(mod_name))
    file_dict.update(get_mod_files_tree_paths_for_loose_mods(mod_name))
    file_dict.update(get_mod_files_persistent_paths_for_loose_mods(mod_name))
    file_dict.update(get_mod_files_mod_name_dir_paths_for_loose_mods(mod_name))

    return file_dict


def get_cooked_mod_file_paths(mod_name: str) -> list:
    return list((get_mod_paths_for_loose_mods(mod_name)).keys())


def get_game_mod_file_paths(mod_name: str) -> list:
    return list((get_mod_paths_for_loose_mods(mod_name)).values())


def get_mod_file_paths_for_manually_made_pak_mods_asset_paths(mod_name: str) -> dict:
    file_dict = {}
    cooked_uproject_dir = unreal_engine.get_cooked_uproject_dir(
        settings.get_uproject_file(), settings.get_unreal_engine_dir()
    )
    mod_info = get_mod_pak_entry(mod_name)
    if mod_info["file_includes"]["asset_paths"] is not None:
        for asset in mod_info["file_includes"]["asset_paths"]:
            base_path = f"{cooked_uproject_dir}/{asset}"
            for extension in file_io.get_file_extensions(base_path):
                before_path = f"{base_path}{extension}"
                after_path = f"{settings.get_working_dir()}/{mod_name}/{unreal_engine.get_uproject_name(settings.get_uproject_file())}/{asset}{extension}"
                file_dict[before_path] = after_path
    return file_dict


def get_mod_file_paths_for_manually_made_pak_mods_tree_paths(mod_name: str) -> dict:
    file_dict = {}
    cooked_uproject_dir = unreal_engine.get_cooked_uproject_dir(
        settings.get_uproject_file(), settings.get_unreal_engine_dir()
    )
    mod_info = get_mod_pak_entry(mod_name)
    if mod_info["file_includes"]["tree_paths"] is not None:
        for tree in mod_info["file_includes"]["tree_paths"]:
            tree_path = f"{cooked_uproject_dir}/{tree}"
            for entry in file_io.get_files_in_tree(tree_path):
                if os.path.isfile(entry):
                    base_entry = os.path.splitext(entry)[0]
                    for extension in file_io.get_file_extensions(base_entry):
                        before_path = f"{base_entry}{extension}"
                        relative_path = os.path.relpath(base_entry, cooked_uproject_dir)
                        after_path = f"{settings.get_working_dir()}/{mod_name}/{unreal_engine.get_uproject_name(settings.get_uproject_file())}/{relative_path}{extension}"
                        file_dict[before_path] = after_path
    return file_dict


def get_mod_file_paths_for_manually_made_pak_mods_persistent_paths(
    mod_name: str,
) -> dict:
    file_dict = {}
    persistent_mod_dir = settings.get_persistent_mod_dir(mod_name)

    for root, _, files in os.walk(persistent_mod_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, persistent_mod_dir)
            game_dir = settings.get_working_dir()
            game_dir = os.path.dirname(game_dir)
            game_dir_path = f"{settings.get_working_dir()}/{mod_name}/{relative_path}"
            file_dict[file_path] = game_dir_path
    return file_dict


def get_mod_file_paths_for_manually_made_pak_mods_mod_name_dir_paths(
    mod_name: str,
) -> dict:
    file_dict = {}
    cooked_game_name_mod_dir = f"{unreal_engine.get_cooked_uproject_dir(settings.get_uproject_file(), settings.get_unreal_engine_dir())}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}"
    for file in file_io.get_files_in_tree(cooked_game_name_mod_dir):
        relative_file_path = os.path.relpath(file, cooked_game_name_mod_dir)
        before_path = f"{cooked_game_name_mod_dir}/{relative_file_path}"
        if settings.get_is_using_alt_dir_name():
            dir_name = settings.get_alt_packing_dir_name()
        else:
            dir_name = unreal_engine.get_uproject_name(settings.get_uproject_file())
        after_path = f"{settings.get_working_dir()}/{mod_name}/{dir_name}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}/{relative_file_path}"
        file_dict[before_path] = after_path
    return file_dict


def get_mod_file_paths_for_manually_made_pak_mods(mod_name: str) -> dict:
    file_dict = {}
    file_dict.update(
        get_mod_file_paths_for_manually_made_pak_mods_asset_paths(mod_name)
    )
    file_dict.update(get_mod_file_paths_for_manually_made_pak_mods_tree_paths(mod_name))
    file_dict.update(
        get_mod_file_paths_for_manually_made_pak_mods_persistent_paths(mod_name)
    )
    file_dict.update(
        get_mod_file_paths_for_manually_made_pak_mods_mod_name_dir_paths(mod_name)
    )

    return file_dict
