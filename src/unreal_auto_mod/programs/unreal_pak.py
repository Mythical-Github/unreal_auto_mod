import os
import shutil

from rich.progress import Progress

import unreal_auto_mod.app_runner
import unreal_auto_mod.settings
from unreal_auto_mod import file_io, packing, utilities
from unreal_auto_mod.data_structures import CompressionType
from unreal_auto_mod.programs import unreal_engine


def get_pak_dir_to_pack(mod_name: str):
    return f"{unreal_auto_mod.settings.get_working_dir()}/{mod_name}"


def make_response_file_iostore(mod_name: str) -> str:
    file_list_path = os.path.join(
        unreal_auto_mod.settings.get_working_dir(), f"{mod_name}_filelist.txt"
    )
    dir_to_pack = get_pak_dir_to_pack(mod_name)
    processed_base_paths = set()

    with open(file_list_path, "w") as file:
        for root, _, files in os.walk(dir_to_pack):
            for file_name in files:
                absolute_path = os.path.join(root, file_name)
                if not os.path.isfile(absolute_path):
                    file_not_found_error = (
                        f'The following file could not be found "{absolute_path}"'
                    )
                    raise FileNotFoundError(file_not_found_error)

                base_path = os.path.splitext(absolute_path)[0]
                if base_path in processed_base_paths:
                    continue

                processed_base_paths.add(base_path)

                relative_path = os.path.relpath(root, dir_to_pack).replace("\\", "/")
                mount_point = f"../../../{relative_path}/"
                file.write(f'"{os.path.normpath(absolute_path)}" "{mount_point}"\n')
    return file_list_path


def make_response_file_non_iostore(mod_name: str) -> str:
    file_list_path = os.path.join(
        unreal_auto_mod.settings.get_working_dir(), f"{mod_name}_filelist.txt"
    )
    dir_to_pack = get_pak_dir_to_pack(mod_name)
    with open(file_list_path, "w") as file:
        for root, _, files in os.walk(dir_to_pack):
            for file_name in files:
                absolute_path = os.path.join(root, file_name)
                if not os.path.isfile:
                    file_not_found_error = (
                        f'The following file could not be found "{absolute_path}"'
                    )
                    raise FileNotFoundError(file_not_found_error)
                relative_path = os.path.relpath(root, dir_to_pack).replace("\\", "/")
                mount_point = f"../../../{relative_path}/"
                file.write(f'"{os.path.normpath(absolute_path)}" "{mount_point}"\n')
    return file_list_path


def get_iostore_commands_file_contents(mod_name: str, final_pak_file: str) -> str:
    chunk_utoc = os.path.normpath(f"{os.path.dirname(final_pak_file)}/{mod_name}.utoc")
    container_name = mod_name
    response_file = make_response_file_iostore(mod_name)
    return f'''-Output="{chunk_utoc}" -ContainerName={container_name} -ResponseFile="{response_file}"'''


def make_iostore_unreal_pak_mod_checks(
    cooked_content_dir: str,
    global_utoc_path: str,
    crypto_keys_json: str,
    commands_txt_path: str,
):
    file_io.check_directory_exists(cooked_content_dir)
    file_io.check_file_exists(global_utoc_path)
    file_io.check_file_exists(crypto_keys_json)
    file_io.check_file_exists(commands_txt_path)


# def make_ue4_iostore_mod(mod_name: str, final_pak_file: str, use_symlinks: bool):
def make_ue4_iostore_mod(mod_name: str, final_pak_file: str):
    unreal_engine_dir = unreal_auto_mod.settings.get_unreal_engine_dir()
    # unreal_pak = unreal_engine.get_unreal_pak_exe_path(unreal_engine_dir)
    exe = unreal_engine.get_editor_cmd_path(unreal_engine_dir)
    ue_win_dir_str = unreal_engine.get_win_dir_str(unreal_engine_dir)
    uproject_name = os.path.splitext(
        os.path.basename(unreal_auto_mod.settings.get_uproject_file())
    )[0]
    global_utoc_path = f"{utilities.get_uproject_dir()}/Saved/StagedBuilds/{ue_win_dir_str}/{uproject_name}/Content/Paks/global.utoc"
    cooked_content_dir = f"{unreal_auto_mod.settings.get_working_dir()}/{mod_name}"

    commands_txt_content = get_iostore_commands_file_contents(mod_name, final_pak_file)
    commands_txt_path = f"{unreal_auto_mod.settings.get_working_dir()}/iostore_packaging/{mod_name}_commands_list.txt"
    os.makedirs(os.path.dirname(commands_txt_path), exist_ok=True)
    with open(commands_txt_path, "w") as file:
        file.write(commands_txt_content)

    crypto_keys_json = f"{utilities.get_uproject_dir()}/Saved/Cooked/{ue_win_dir_str}/{uproject_name}/Metadata/Crypto.json"

    make_iostore_unreal_pak_mod_checks(
        cooked_content_dir, global_utoc_path, crypto_keys_json, commands_txt_path
    )

    platform_string = unreal_engine.get_win_dir_str(
        unreal_auto_mod.settings.get_unreal_engine_dir()
    )
    iostore_txt_location = f"{unreal_auto_mod.settings.get_working_dir()}/iostore_packaging/{mod_name}_iostore.txt"
    # default_engine_patch_padding_alignment = 2048
    args = [
        # unreal_pak,
        f'"{unreal_auto_mod.settings.get_uproject_file()}"',
        "-run=IoStore",
        f'-CreateGlobalContainer="{os.path.normpath(global_utoc_path)}"',
        f'-CookedDirectory="{os.path.normpath(cooked_content_dir)}"',
        f'-Commands="{os.path.normpath(commands_txt_path)}"',
        # f'-CookerOrder="{os.path.normpath(cooker_order_file)}"',
        # f'-patchpaddingalign={default_engine_patch_padding_alignment}',
        "-NoDirectoryIndex",
        # f'-cryptokeys="{os.path.normpath(crypto_keys_json)}"',
        f"-TargetPlatform={platform_string}",
        f'-abslog="{iostore_txt_location}"',
        "-stdout",
        "-CrashForUAT",
        "-unattended",
        "-NoLogTimes",
        "-UTF8Output",
    ]
    unreal_auto_mod.app_runner.run_app(exe_path=exe, args=args)


# def make_ue5_iostore_mods(mod_name: str, final_pak_file: str, use_symlinks: bool):


def make_ue5_iostore_mods(mod_name: str, final_pak_file: str):
    unreal_engine_dir = unreal_auto_mod.settings.get_unreal_engine_dir()
    # unreal_pak = unreal_engine.get_unreal_pak_exe_path(unreal_engine_dir)
    exe = unreal_engine.get_editor_cmd_path(unreal_engine_dir)
    ue_win_dir_str = unreal_engine.get_win_dir_str(unreal_engine_dir)
    uproject_name = os.path.splitext(
        os.path.basename(unreal_auto_mod.settings.get_uproject_file())
    )[0]
    global_utoc_path = f"{utilities.get_uproject_dir()}/Saved/StagedBuilds/{ue_win_dir_str}/{uproject_name}/Content/Paks/global.utoc"
    cooked_content_dir = f"{unreal_auto_mod.settings.get_working_dir()}/{mod_name}"

    commands_txt_content = get_iostore_commands_file_contents(mod_name, final_pak_file)
    commands_txt_path = f"{unreal_auto_mod.settings.get_working_dir()}/iostore_packaging/{mod_name}_commands_list.txt"
    os.makedirs(os.path.dirname(commands_txt_path), exist_ok=True)
    with open(commands_txt_path, "w") as file:
        file.write(commands_txt_content)

    meta_data_dir = f"{utilities.get_uproject_dir()}/Saved/Cooked/{ue_win_dir_str}/{uproject_name}/Metadata"
    crypto_keys_json = f"{meta_data_dir}/Crypto.json"
    script_objects_bin = f"{meta_data_dir}/scriptobjects.bin"
    package_store_manifest = f"{meta_data_dir}/packagestore.manifest"

    make_iostore_unreal_pak_mod_checks(
        cooked_content_dir, global_utoc_path, crypto_keys_json, commands_txt_path
    )

    platform_string = unreal_engine.get_win_dir_str(
        unreal_auto_mod.settings.get_unreal_engine_dir()
    )
    iostore_txt_location = f"{unreal_auto_mod.settings.get_working_dir()}/iostore_packaging/{mod_name}_iostore.txt"
    # default_engine_patch_padding_alignment = 2048
    args = [
        # f'"{unreal_pak}',
        f'"{unreal_auto_mod.settings.get_uproject_file()}"',
        "-run=IoStore",
        f'-CreateGlobalContainer="{os.path.normpath(global_utoc_path)}"',
        f'-CookedDirectory="{os.path.normpath(cooked_content_dir)}"',
        f'-Commands="{os.path.normpath(commands_txt_path)}"',
        f'-PackageStoreManifest="{package_store_manifest}"',
        f'-ScriptObjects="{script_objects_bin}"',
        # f'-CookerOrder="{os.path.normpath(cooker_order_file)}"',
        # f'-patchpaddingalign={default_engine_patch_padding_alignment}',
        "-NoDirectoryIndex",
        # f'-cryptokeys="{os.path.normpath(crypto_keys_json)}"',
        f"-TargetPlatform={platform_string}",
        f'-abslog="{iostore_txt_location}"',
        "-stdout",
        "-CrashForUAT",
        "-unattended",
        "-NoLogTimes",
        "-UTF8Output",
    ]
    unreal_auto_mod.app_runner.run_app(exe_path=exe, args=args)


def make_iostore_unreal_pak_mod(
    mod_name: str, final_pak_file: str, *, use_symlinks: bool
):
    if unreal_engine.is_game_ue4(unreal_auto_mod.settings.get_unreal_engine_dir()):
        make_ue4_iostore_mod(mod_name, final_pak_file)
        # make_ue4_iostore_mod(mod_name, final_pak_file, use_symlinks)
    else:
        make_ue5_iostore_mods(mod_name, final_pak_file)
        # make_ue5_iostore_mods(mod_name, final_pak_file, use_symlinks)


def make_non_iostore_unreal_pak_mod(
    exe_path: str,
    intermediate_pak_file: str,
    mod_name: str,
    compression_str: str,
    final_pak_file: str,
    *,
    use_symlinks: bool,
):
    command = f'{exe_path} "{intermediate_pak_file}" -Create="{make_response_file_non_iostore(mod_name)}"'
    if compression_str != "None":
        command = f"{command} -compress -compressionformat={compression_str}"
    unreal_auto_mod.app_runner.run_app(command)
    if os.path.islink(final_pak_file):
        os.unlink(final_pak_file)
    if os.path.isfile(final_pak_file):
        os.remove(final_pak_file)
    packing.install_mod_sig(mod_name, use_symlinks=use_symlinks)
    if use_symlinks:
        os.symlink(intermediate_pak_file, final_pak_file)
    else:
        shutil.copyfile(intermediate_pak_file, final_pak_file)


def install_unreal_pak_mod(
    mod_name: str, compression_type: CompressionType, *, use_symlinks: bool
):
    move_files_for_packing(mod_name)
    compression_str = CompressionType(compression_type).value
    output_pak_dir = f"{unreal_auto_mod.settings.get_working_dir()}/{utilities.get_pak_dir_structure(mod_name)}"
    intermediate_pak_file = f"{unreal_auto_mod.settings.get_working_dir()}/{utilities.get_pak_dir_structure(mod_name)}/{mod_name}.pak"
    final_pak_file = f"{utilities.custom_get_game_paks_dir()}/{utilities.get_pak_dir_structure(mod_name)}/{mod_name}.pak"
    os.makedirs(output_pak_dir, exist_ok=True)
    os.makedirs(
        f"{utilities.custom_get_game_paks_dir()}/{utilities.get_pak_dir_structure(mod_name)}",
        exist_ok=True,
    )
    exe_path = unreal_engine.get_unreal_pak_exe_path(
        unreal_auto_mod.settings.get_unreal_engine_dir()
    )
    is_game_iostore = unreal_engine.get_is_game_iostore(
        unreal_auto_mod.settings.get_uproject_file(), utilities.custom_get_game_dir()
    )

    if is_game_iostore:
        make_iostore_unreal_pak_mod(mod_name, final_pak_file, use_symlinks=use_symlinks)
    else:
        make_non_iostore_unreal_pak_mod(
            exe_path,
            intermediate_pak_file,
            mod_name,
            compression_str,
            final_pak_file,
            use_symlinks=use_symlinks,
        )


def move_files_for_packing(mod_name: str):
    mod_files_dict = packing.get_mod_file_paths_for_manually_made_pak_mods(mod_name)
    mod_files_dict = utilities.filter_file_paths(mod_files_dict)

    with Progress() as progress:
        task = progress.add_task(
            f"[green]Copying files for {mod_name} mod...", total=len(mod_files_dict)
        )

        for before_file, after_file in mod_files_dict.items():
            if os.path.exists(after_file):
                if not file_io.get_do_files_have_same_hash(before_file, after_file):
                    os.remove(after_file)
            elif not os.path.isdir(os.path.dirname(after_file)):
                os.makedirs(os.path.dirname(after_file))

            if os.path.isfile(before_file):
                shutil.copy2(before_file, after_file)

            progress.update(task, advance=1)
