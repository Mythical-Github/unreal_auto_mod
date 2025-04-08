import os
import shutil

from rich.progress import Progress

from unreal_auto_mod import gen_py_utils as general_utils
from unreal_auto_mod import log_py as log
from unreal_auto_mod import repak_utilities, script_states, settings, ue_dev_py_utils, unreal_pak, utilities
from unreal_auto_mod.enums import CompressionType, PackingType, ScriptStateType, get_enum_from_val

install_queue_types = []
uninstall_queue_types = []
command_queue = []


class PopulateQueueTypeCheckDicts:
    global install_queue_types
    global uninstall_queue_types
    for packing_type in list(PackingType):
        for mod_info in utilities.get_mod_info_list():
            if mod_info['is_enabled'] and mod_info['mod_name'] in settings.mod_names:
                install_queue_type = get_enum_from_val(PackingType, mod_info['packing_type'])
                if install_queue_type not in install_queue_types:
                    install_queue_types.append(install_queue_type)
            if not mod_info['is_enabled'] and mod_info['mod_name'] in settings.mod_names:
                uninstall_queue_type = get_enum_from_val(PackingType, mod_info['packing_type'])
                if uninstall_queue_type not in uninstall_queue_types:
                    uninstall_queue_types.append(uninstall_queue_type)


def get_mod_packing_type(mod_name: str) -> PackingType:
    for mod_pak_info in utilities.get_mod_pak_info_list():
        if mod_name == mod_pak_info['mod_name']:
            return get_enum_from_val(PackingType, mod_pak_info['packing_type'])
    return None


def get_is_mod_name_in_use(mod_name: str) -> bool:
    for mod_pak_info in utilities.get_mod_pak_info_list():
        if mod_name == mod_pak_info['mod_name']:
            return True
    return False


def get_mod_pak_entry(mod_name: str) -> dict:
    for info in utilities.get_mod_pak_info_list():
        if info['mod_name'] == mod_name:
            return dict(info)
    return None


def get_is_mod_installed(mod_name: str) -> bool:
    for info in utilities.get_mod_pak_info_list():
        if info['mod_name'] == mod_name:
            return True
    return False


def get_engine_pak_command() -> str:
    command = (
        f'Engine\\Build\\BatchFiles\\RunUAT.bat BuildCookRun '
        f'-project="{utilities.get_uproject_file()}" '
        f'-noP4 '
        f'-cook '
        f'-iterate '
        f'-stage '
        f'-pak '
        f'-compressed'
    )
    if utilities.get_is_using_unversioned_cooked_content():
        unversioned_arg = '-unversionedcookedcontent'
        command = f'{command} {unversioned_arg}'
    if utilities.get_always_build_project() or not ue_dev_py_utils.has_build_target_been_built(utilities.get_uproject_file()):
        build_arg = '-build'
        command = f'{command} {build_arg}'
    for arg in utilities.get_engine_cook_and_packaging_args():
        command = f'{command} {arg}'
    is_game_iostore = ue_dev_py_utils.get_is_game_iostore(utilities.get_uproject_file(), utilities.custom_get_game_dir())
    if is_game_iostore:
        command = f'{command} -iostore'
        log.log_message('Check: Game is iostore')
    else:
        log.log_message('Check: Game is not iostore')
    return command


# def get_cook_project_command() -> str:
#     command = (
#         f'Engine\\Build\\BatchFiles\\RunUAT.bat BuildCookRun '
#         f'-project="{utilities.get_uproject_file()}" '
#         f'-noP4 '
#         f'-cook '
#         f'-iterate '
#         f'-stage '
#         f'-pak '
#         f'-compressed'
#     )
#     if utilities.get_is_using_unversioned_cooked_content():
#         unversioned_arg = '-unversionedcookedcontent'
#         command = f'{command} {unversioned_arg}'
#     if utilities.get_always_build_project() or not ue_dev_py_utils.ue_dev_py_utils.has_build_target_been_built(utilities.get_uproject_file()):
#         build_arg = '-build'
#         command = f'{command} {build_arg}'
#     for arg in utilities.get_engine_cook_and_packaging_args():
#         command = f'{command} {arg}'
#     is_game_iostore = ue_dev_py_utils.ue_dev_py_utils.get_is_game_iostore(utilities.get_uproject_file(), utilities.custom_get_game_dir())
#     if is_game_iostore:
#         command = f'{command} -iostore'
#         log.log_message('Check: Game is iostore')
#     else:
#         log.log_message('Check: Game is not iostore')
#     return command


def get_cook_project_command() -> str:
    command = (
        f'Engine\\Build\\BatchFiles\\RunUAT.bat BuildCookRun '
        f'-project="{utilities.get_uproject_file()}" '
        f'-noP4 '
        f'-cook '
        f'-iterate '
        f'-skipstage '
        # f'-nocompileeditor '
        f'-nodebuginfo'
    )
    if utilities.get_is_using_unversioned_cooked_content():
        unversioned_arg = '-unversionedcookedcontent'
        command = f'{command} {unversioned_arg}'
    if utilities.get_always_build_project() or not ue_dev_py_utils.has_build_target_been_built(utilities.get_uproject_file()):
        build_arg = '-build'
        command = f'{command} {build_arg}'
    for arg in utilities.get_engine_cook_and_packaging_args():
        command = f'{command} {arg}'
    return command


def cook_uproject():
    run_proj_command(get_cook_project_command())


def package_uproject():
    run_proj_command(get_engine_pak_command())


# def run_proj_command(command: str):
#     utilities.run_app(command, working_dir=utilities.get_unreal_engine_dir())


def run_proj_command(command: str):
    command_parts = command.split(' ')
    executable = command_parts[0]
    args = command_parts[1:]
    utilities.run_app(exe_path=executable, args=args, working_dir=utilities.get_unreal_engine_dir())



def handle_uninstall_logic(packing_type: PackingType):
    for mod_pak_info in utilities.get_mod_info_list():
        if not mod_pak_info['is_enabled'] and mod_pak_info['mod_name'] in settings.mod_names:
            if get_enum_from_val(PackingType, mod_pak_info['packing_type']) == packing_type:
                uninstall_mod(packing_type, mod_pak_info['mod_name'])


def handle_install_logic(packing_type: PackingType):
    script_states.ScriptState.set_script_state(ScriptStateType.PRE_PAK_DIR_SETUP)
    for mod_pak_info in utilities.get_mod_info_list():
        if mod_pak_info['is_enabled'] and mod_pak_info['mod_name'] in settings.mod_names:
            if get_enum_from_val(PackingType, mod_pak_info['packing_type']) == packing_type:
                install_mod(packing_type, mod_pak_info['mod_name'],
                            get_enum_from_val(CompressionType, mod_pak_info['compression_type']))
    script_states.ScriptState.set_script_state(ScriptStateType.POST_PAK_DIR_SETUP)
    for command in command_queue:
        utilities.run_app(command)



def make_mods():
    if utilities.get_clear_uproject_saved_cooked_dir_before_tests():
        cooked_dir = ue_dev_py_utils.get_saved_cooked_dir(utilities.get_uproject_file())
        if os.path.isdir(cooked_dir):
            shutil.rmtree(cooked_dir)
    cooking()

    global uninstall_queue_types
    script_states.ScriptState.set_script_state(ScriptStateType.PRE_MODS_UNINSTALL)
    for uninstall_queue_type in uninstall_queue_types:
        handle_uninstall_logic(uninstall_queue_type)
    script_states.ScriptState.set_script_state(ScriptStateType.POST_MODS_UNINSTALL)

    script_states.ScriptState.set_script_state(ScriptStateType.PRE_MODS_INSTALL)
    global install_queue_types
    for install_queue_type in install_queue_types:
        handle_install_logic(install_queue_type)
    script_states.ScriptState.set_script_state(ScriptStateType.POST_MODS_INSTALL)


def uninstall_loose_mod(mod_name: str):
    mod_files = get_mod_paths_for_loose_mods(mod_name)
    dict_keys = mod_files.keys()
    for key in dict_keys:
        file_to_remove = mod_files[key]
        if os.path.isfile(file_to_remove):
            os.remove(file_to_remove)

    for folder in set(os.path.dirname(file) for file in mod_files.values()):
        if os.path.exists(folder) and not os.listdir(folder):
            os.removedirs(folder)


def uninstall_pak_mod(mod_name: str):
    extensions = ue_dev_py_utils.get_game_pak_folder_archives(utilities.get_uproject_file(), utilities.custom_get_game_dir())
    if ue_dev_py_utils.is_game_ue5(utilities.get_unreal_engine_dir()):
        extensions.extend(['ucas', 'utoc'])
    for extension in extensions:
        file_path = os.path.join(utilities.custom_get_game_paks_dir(), utilities.get_pak_dir_structure(mod_name), f'{mod_name}.{extension}')
        if os.path.isfile(file_path):
            os.remove(file_path)


def uninstall_mod(packing_type: PackingType, mod_name: str):
    if packing_type == PackingType.LOOSE:
        uninstall_loose_mod(mod_name)
    elif packing_type in list(PackingType):
        uninstall_pak_mod(mod_name)


def install_loose_mod(mod_name: str):
    mod_files = get_mod_paths_for_loose_mods(mod_name)
    dict_keys = mod_files.keys()
    for key in dict_keys:
        before_file = key
        after_file = mod_files[key]
        _dir = os.path.dirname(after_file)
        if not os.path.isdir(_dir):
            os.makedirs(_dir)
        if os.path.exists(before_file):
            if os.path.isfile(before_file):
                shutil.copyfile(before_file, after_file)



def install_engine_mod(mod_name: str):
    mod_files = []
    info = utilities.get_mod_pak_info(mod_name)
    pak_chunk_num = info['pak_chunk_num']
    prefix = f'{ue_dev_py_utils.get_uproject_dir(utilities.get_uproject_file())}/Saved/StagedBuilds/{ue_dev_py_utils.get_win_dir_str(utilities.get_unreal_engine_dir())}/{ue_dev_py_utils.get_uproject_name(utilities.get_uproject_file())}/Content/Paks/pakchunk{pak_chunk_num}-{ue_dev_py_utils.get_win_dir_str(utilities.get_unreal_engine_dir())}.'
    mod_files.append(prefix)
    for file in mod_files:
        for suffix in ue_dev_py_utils.get_game_pak_folder_archives(utilities.get_uproject_file(), utilities.custom_get_game_dir()):
            before_file = f'{file}{suffix}'
            dir_engine_mod = f'{utilities.custom_get_game_dir()}/Content/Paks/{utilities.get_pak_dir_structure(mod_name)}'
            if not os.path.isdir(dir_engine_mod):
                os.makedirs(dir_engine_mod)
            after_file = f'{dir_engine_mod}/{mod_name}.{suffix}'
            if os.path.exists(after_file):
                if not general_utils.get_do_files_have_same_hash(before_file, after_file):
                    os.remove(after_file)
                    shutil.copy2(before_file, after_file)
            else:
                shutil.copy2(before_file, after_file)


def make_pak_repak(mod_name: str):
    pak_dir = f'{utilities.custom_get_game_paks_dir()}/{utilities.get_pak_dir_structure(mod_name)}'
    if not os.path.isdir(pak_dir):
        os.makedirs(pak_dir)
    os.chdir(pak_dir)

    compression_type_str = utilities.get_mod_pak_info(mod_name)['compression_type']
    before_symlinked_dir = f'{utilities.get_working_dir()}/{mod_name}'

    if not os.path.isdir(before_symlinked_dir) or not os.listdir(before_symlinked_dir):
        from unreal_auto_mod import log_py as log
        log.log_message(f'Error: {before_symlinked_dir}')
        log.log_message('Error: does not exist or is empty, indicating a packaging and/or config issue')
        raise FileNotFoundError


    command = f'"{repak_utilities.get_package_path()}" pack "{before_symlinked_dir}" "{pak_dir}/{mod_name}.pak"'
    if compression_type_str != 'None':
        command = f'{command} --compression {compression_type_str} --version {repak_utilities.get_repak_pak_version_str()}'
    if os.path.isfile(f'{pak_dir}/{mod_name}.pak'):
        os.remove(f'{pak_dir}/{mod_name}.pak')
    command_queue.append(command)


def install_repak_mod(mod_name: str):
    mod_files_dict = get_mod_file_paths_for_manually_made_pak_mods(mod_name)
    mod_files_dict = utilities.filter_file_paths(mod_files_dict)

    with Progress() as progress:
        task = progress.add_task(f"[green]Copying files for {mod_name} mod...", total=len(mod_files_dict))

        for before_file, after_file in mod_files_dict.items():
            if os.path.exists(after_file):
                if not general_utils.get_do_files_have_same_hash(before_file, after_file):
                    os.remove(after_file)
            if not os.path.isdir(os.path.dirname(after_file)):
                os.makedirs(os.path.dirname(after_file))
            if os.path.isfile(before_file):
                shutil.copy2(before_file, after_file)

            progress.update(task, advance=1)
    make_pak_repak(mod_name)


def install_mod(packing_type: PackingType, mod_name: str, compression_type: CompressionType):
    if packing_type == PackingType.LOOSE:
        install_loose_mod(mod_name)
    if packing_type == PackingType.ENGINE:
        install_engine_mod(mod_name)
    if packing_type == PackingType.REPAK:
        install_repak_mod(mod_name)
    if packing_type == PackingType.UNREAL_PAK:
        unreal_pak.install_unreal_pak_mod(mod_name, compression_type)


def cooking():
    if not utilities.get_should_ship_uproject_steps():
        script_states.ScriptState.set_script_state(ScriptStateType.PRE_COOKING)
        if PackingType.ENGINE not in install_queue_types:
            cook_uproject()
        else:
            package_uproject()
        script_states.ScriptState.set_script_state(ScriptStateType.POST_COOKING)


def get_mod_files_asset_paths_for_loose_mods(mod_name: str) -> dict:
    file_dict = {}
    cooked_uproject_dir = ue_dev_py_utils.get_cooked_uproject_dir(utilities.get_uproject_file(), utilities.get_unreal_engine_dir())
    mod_pak_info = get_mod_pak_entry(mod_name)
    for asset in mod_pak_info['manually_specified_assets']['asset_paths']:
        base_path = f'{cooked_uproject_dir}/{asset}'
        for extension in general_utils.get_file_extensions(base_path):
            before_path = f'{base_path}{extension}'
            after_path = f'{utilities.custom_get_game_dir()}/{asset}{extension}'
            file_dict[before_path] = after_path
    return file_dict


def get_mod_files_tree_paths_for_loose_mods(mod_name: str) -> dict:
    file_dict = {}
    cooked_uproject_dir = ue_dev_py_utils.get_cooked_uproject_dir(utilities.get_uproject_file(), utilities.get_unreal_engine_dir())
    mod_pak_info = get_mod_pak_entry(mod_name)
    for tree in mod_pak_info['manually_specified_assets']['tree_paths']:
        tree_path = f'{cooked_uproject_dir}/{tree}'
        for entry in general_utils.get_files_in_tree(tree_path):
            if os.path.isfile(entry):
                base_entry = os.path.splitext(entry)[0]
                for extension in general_utils.get_file_extensions_two(entry):
                    before_path = f'{base_entry}{extension}'
                    relative_path = os.path.relpath(base_entry, cooked_uproject_dir)
                    after_path = f'{utilities.custom_get_game_dir()}/{relative_path}{extension}'
                    file_dict[before_path] = after_path
    return file_dict


def get_mod_files_persistent_paths_for_loose_mods(mod_name: str) -> dict:
    file_dict = {}
    persistent_mod_dir = utilities.get_persistant_mod_dir(mod_name)

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
    cooked_game_name_mod_dir = f'{ue_dev_py_utils.get_cooked_uproject_dir(utilities.get_uproject_file(), utilities.get_unreal_engine_dir())}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}'
    for file in general_utils.get_files_in_tree(cooked_game_name_mod_dir):
        relative_file_path = os.path.relpath(file, cooked_game_name_mod_dir)
        before_path = f'{cooked_game_name_mod_dir}/{relative_file_path}'
        after_base = utilities.custom_get_game_dir()
        after_path = f'{after_base}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}/{relative_file_path}'
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
    if not utilities.get_should_ship_uproject_steps():
        cooked_uproject_dir = ue_dev_py_utils.get_cooked_uproject_dir(utilities.get_uproject_file(), utilities.get_unreal_engine_dir())
        mod_pak_info = get_mod_pak_entry(mod_name)
        if mod_pak_info['manually_specified_assets']['asset_paths'] is not None:
            for asset in mod_pak_info['manually_specified_assets']['asset_paths']:
                base_path = f'{cooked_uproject_dir}/{asset}'
                for extension in general_utils.get_file_extensions(base_path):
                    before_path = f'{base_path}{extension}'
                    after_path = f'{utilities.get_working_dir()}/{mod_name}/{ue_dev_py_utils.get_uproject_name(utilities.get_uproject_file())}/{asset}{extension}'
                    file_dict[before_path] = after_path
    return file_dict


def get_mod_file_paths_for_manually_made_pak_mods_tree_paths(mod_name: str) -> dict:
    file_dict = {}
    if not utilities.get_should_ship_uproject_steps():
        cooked_uproject_dir = ue_dev_py_utils.get_cooked_uproject_dir(utilities.get_uproject_file(), utilities.get_unreal_engine_dir())
        mod_pak_info = get_mod_pak_entry(mod_name)
        if mod_pak_info['manually_specified_assets']['tree_paths'] is not None:
            for tree in mod_pak_info['manually_specified_assets']['tree_paths']:
                tree_path = f'{cooked_uproject_dir}/{tree}'
                for entry in general_utils.get_files_in_tree(tree_path):
                    if os.path.isfile(entry):
                        base_entry = os.path.splitext(entry)[0]
                        for extension in general_utils.get_file_extensions(base_entry):
                            before_path = f'{base_entry}{extension}'
                            relative_path = os.path.relpath(base_entry, cooked_uproject_dir)
                            after_path = f'{utilities.get_working_dir()}/{mod_name}/{ue_dev_py_utils.get_uproject_name(utilities.get_uproject_file())}/{relative_path}{extension}'
                            file_dict[before_path] = after_path
    return file_dict


def get_mod_file_paths_for_manually_made_pak_mods_persistent_paths(mod_name: str) -> dict:
    file_dict = {}
    persistent_mod_dir = utilities.get_persistant_mod_dir(mod_name)

    for root, _, files in os.walk(persistent_mod_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, persistent_mod_dir)
            game_dir = utilities.get_working_dir()
            game_dir = os.path.dirname(game_dir)
            game_dir_path = f'{utilities.get_working_dir()}/{mod_name}/{relative_path}'
            file_dict[file_path] = game_dir_path
    return file_dict


def get_mod_file_paths_for_manually_made_pak_mods_mod_name_dir_paths(mod_name: str) -> dict:
    file_dict = {}
    if not utilities.get_should_ship_uproject_steps():
        cooked_game_name_mod_dir = f'{ue_dev_py_utils.get_cooked_uproject_dir(utilities.get_uproject_file(), utilities.get_unreal_engine_dir())}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}'
        for file in general_utils.get_files_in_tree(cooked_game_name_mod_dir):
            relative_file_path = os.path.relpath(file, cooked_game_name_mod_dir)
            before_path = f'{cooked_game_name_mod_dir}/{relative_file_path}'
            if utilities.get_is_using_alt_dir_name():
                dir_name = utilities.get_alt_packing_dir_name()
            else:
                dir_name = ue_dev_py_utils.get_uproject_name(utilities.get_uproject_file())
            after_path = f'{utilities.get_working_dir()}/{mod_name}/{dir_name}/Content/{utilities.get_unreal_mod_tree_type_str(mod_name)}/{utilities.get_mod_name_dir_name(mod_name)}/{relative_file_path}'
            file_dict[before_path] = after_path
    return file_dict


def get_mod_file_paths_for_manually_made_pak_mods(mod_name: str) -> dict:
    file_dict = {}
    file_dict.update(get_mod_file_paths_for_manually_made_pak_mods_asset_paths(mod_name))
    file_dict.update(get_mod_file_paths_for_manually_made_pak_mods_tree_paths(mod_name))
    file_dict.update(get_mod_file_paths_for_manually_made_pak_mods_persistent_paths(mod_name))
    file_dict.update(get_mod_file_paths_for_manually_made_pak_mods_mod_name_dir_paths(mod_name))

    return file_dict
