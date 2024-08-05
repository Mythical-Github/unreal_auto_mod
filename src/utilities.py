import glob
import hashlib
import json
import os
import shutil
import subprocess

import settings
from enums import PackagingDirType, ExecutionMode, ScriptStateType, CompressionType, get_enum_from_val
from python_logging import log
import general_utils
import unreal_dev_utils


def get_game_info_launch_type_enum_str_value() -> str:
    return settings.settings['game_info']['launch_type']


def get_game_id() -> int:
    return settings.settings['game_info']['game_id']


def get_game_launcher_exe_path() -> str:
    return settings.settings['game_info']['game_launcher_exe']


def get_game_launch_params() -> list:
    return settings.settings['game_info']['launch_params']


def get_override_automatic_launcher_exe_finding() -> bool:
    return settings.settings['game_info']['override_automatic_launcher_exe_finding']


def get_auto_move_windows():
    return settings.settings["auto_move_windows"]


def get_engine_launch_args() -> list:
    return settings.settings['engine_info']['engine_launch_args']


def get_alt_exe_methods() -> list:
    return settings.settings['alt_exe_methods']


def get_is_using_unversioned_cooked_content() -> bool:
    return settings.settings['engine_info']['use_unversioned_cooked_content']


def get_mod_info_list() -> list:
    return settings.settings['mod_pak_info']


def get_game_exe_path() -> str:
    game_exe_path = settings.settings['game_info']['game_exe_path']
    general_utils.check_file_exists(game_exe_path)
    return game_exe_path


def get_is_using_alt_dir_name() -> bool:
    return settings.settings['alt_uproject_name_in_game_dir']['use_alt_method']


def get_alt_packing_dir_name() -> str:
    return settings.settings['alt_uproject_name_in_game_dir']['name']


def get_game_process_name():
    return unreal_dev_utils.get_game_process_name(get_game_exe_path())


def get_process_to_kill_info_list() -> list:
    return settings.settings['process_kill_info']['processes']


def kill_processes(state: ScriptStateType):
    current_state = state.value if isinstance(state, ScriptStateType) else state
    for process_info in get_process_to_kill_info_list():
        target_state = process_info.get('script_state')
        if target_state == current_state:
            if process_info['use_substring_check']:
                proc_name_substring = process_info['process_name']
                for proc_info in general_utils.get_processes_by_substring(proc_name_substring):
                    proc_name = proc_info['name']
                    general_utils.kill_process(proc_name)
            else:
                proc_name = process_info['process_name']
                general_utils.kill_process(proc_name)


def get_override_automatic_version_finding() -> bool:
    return settings.settings['engine_info']['override_automatic_version_finding']


def custom_get_unreal_engine_version(engine_path: str) -> str:
    if get_override_automatic_version_finding():
        unreal_engine_major_version = settings.settings['engine_info']['unreal_engine_major_version']
        unreal_engine_minor_version = settings.settings['engine_info']['unreal_engine_minor_version']
        return f'{unreal_engine_major_version}.{unreal_engine_minor_version}'
    else:
        return unreal_dev_utils.get_unreal_engine_version(engine_path)
    

def custom_get_game_dir():
    return unreal_dev_utils.get_game_dir(get_game_exe_path())


# port out
def get_game_content_dir():
    return f'{custom_get_game_dir()}/Content'

# port out
def get_game_paks_dir() -> str:
    alt_game_dir = os.path.dirname(custom_get_game_dir())
    if get_is_using_alt_dir_name():
        _dir = f'{alt_game_dir}/{get_alt_packing_dir_name()}/Content/Paks'
    else:
        _dir = f'{alt_game_dir}/{get_uproject_name()}/Content/Paks'
    return _dir


def get_unreal_engine_dir() -> str:
    ue_dir = settings.settings['engine_info']['unreal_engine_dir']
    general_utils.check_file_exists(ue_dir)
    return ue_dir

# port out
def get_win_dir_type() -> PackagingDirType:
    if custom_get_unreal_engine_version(get_unreal_engine_dir()).startswith('5'):
        return PackagingDirType.WINDOWS
    else:
        return PackagingDirType.WINDOWS_NO_EDITOR

# port out
def is_game_ue5() -> bool:
    return get_win_dir_type() == PackagingDirType.WINDOWS

# port out
def is_game_ue4() -> bool:
    return get_win_dir_type() == PackagingDirType.WINDOWS_NO_EDITOR

# port out
def get_file_hash(file_path: str) -> str:
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()

# port out
def get_do_files_have_same_hash(file_path_one: str, file_path_two: str) -> bool:
    if os.path.exists(file_path_one) and os.path.exists(file_path_two):
        hash_one = get_file_hash(file_path_one)
        hash_two = get_file_hash(file_path_two)
        return hash_one == hash_two
    else:
        return False

# port out
def get_unreal_editor_exe_path() -> str:
    if get_win_dir_type() == PackagingDirType.WINDOWS_NO_EDITOR:
        engine_path_suffix = 'UE4Editor.exe'
    else:
        engine_path_suffix = 'UnrealEditor.exe'
    return f'{get_unreal_engine_dir()}/Engine/Binaries/Win64/{engine_path_suffix}'


def is_toggle_engine_during_testing_in_use() -> bool:
    return settings.settings['engine_info']['toggle_engine_during_testing']


# port out
def run_app(exe_path: str, exec_mode: ExecutionMode = ExecutionMode.SYNC, args: list = [], working_dir: str = None):
    if exec_mode == ExecutionMode.SYNC:
        command = exe_path
        for arg in args:
            command = f'{command} {arg}'
        if working_dir:
            command = f'{working_dir}/{command}'
        log.log_message(f'Command: {command} running with the {exec_mode} enum')
        if working_dir:
            if os.path.isdir(working_dir):
                os.chdir(working_dir)

        process = subprocess.Popen(command, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
        
        for line in iter(process.stdout.readline, ''):
            log.log_message(line.strip())

        process.stdout.close()
        process.wait()
        log.log_message(f'Command: {command} finished')

    elif exec_mode == ExecutionMode.ASYNC:
        command = exe_path
        command = f'"{command}"'
        for arg in args:
            command = f'{command} {arg}'
        log.log_message(f'Command: {command} started with the {exec_mode} enum')
        subprocess.Popen(command, cwd=working_dir, start_new_session=True, shell=True)

# port out
def get_engine_window_title() -> str:
    return f'{general_utils.get_process_name(get_uproject_file())[:-9]} - {'Unreal Editor'}'

# port out
def get_engine_process_name() -> str:
    return general_utils.get_process_name(get_unreal_editor_exe_path())

# port out
def get_files_in_tree(tree_path: str) -> list:
    return glob.glob(tree_path + '/**/*', recursive=True)

# port out
def get_file_extension(file_path: str) -> str:
    _, file_extension = os.path.splitext(file_path)
    return file_extension

# port out
# returns .extension not extension
def get_file_extensions(file_path: str) -> list:
    extensions = []
    files = get_files_in_tree(file_path)
    for file in files:
        extensions.append(get_file_extension(file))
    return extensions

# port out
# returns extension, not .extension
def get_file_extensions_two(directory_with_base_name: str) -> list:
    directory, base_name = os.path.split(directory_with_base_name)
    extensions = set()
    for _, files in os.walk(directory):
        for file in files:
            if file.startswith(base_name):
                _, ext = os.path.splitext(file)
                if ext:
                    extensions.add(ext)
    return list(extensions)


def get_uproject_file() -> str:
    uproject_file = settings.settings['engine_info']['unreal_project_file']
    general_utils.check_file_exists(uproject_file)
    return uproject_file

# port out
def get_uproject_name() -> str:
    return os.path.splitext(os.path.basename(get_uproject_file()))[0]

# port out
def get_uproject_dir() -> str:
    return os.path.dirname(get_uproject_file())

# port out
def get_saved_cooked_dir() -> str:
    return f'{get_uproject_dir()}/Saved/Cooked'

# port out
def get_win_dir_str() -> str:
    win_dir_type = 'Windows'
    if is_game_ue4():
        win_dir_type = f'{win_dir_type}NoEditor'
    return win_dir_type

# port out
def get_cooked_uproject_dir() -> str:
    return f'{get_uproject_dir()}/Saved/Cooked/{get_win_dir_str()}/{get_uproject_name()}'


def get_use_mod_name_dir_name_override(mod_name: str) -> bool:
    return get_mod_pak_info(mod_name)['use_mod_name_dir_name_override']


def get_mod_name_dir_name_override(mod_name: str) -> bool:
    return get_mod_pak_info(mod_name)['mod_name_dir_name_override']


def get_mod_name_dir_name(mod_name: str) -> str:
    if get_use_mod_name_dir_name_override(mod_name):
        return get_mod_name_dir_name_override(mod_name)
    else:
        return mod_name


def get_mod_pak_info_list() -> list:
    return settings.settings['mod_pak_info']


def get_pak_dir_structure(mod_name: str) -> str:
    for info in get_mod_pak_info_list():
        if info['mod_name'] == mod_name:
            return info['pak_dir_structure']
    return None


def get_mod_compression_type(mod_name: str) -> CompressionType:
    for info in get_mod_pak_info_list():
        if info['mod_name'] == mod_name:
            compresion_str = info['compression_type']
            return get_enum_from_val(CompressionType, compresion_str)
    return None


def get_unreal_mod_tree_type_str(mod_name: str) -> str:
    for info in get_mod_pak_info_list():
        if info['mod_name'] == mod_name:
            return info['mod_name_dir_type']
    return None


def get_mod_pak_info(mod_name: str) -> dict:
    for info in get_mod_pak_info_list():
        if info['mod_name'] == mod_name:
            return dict(info)
    return None


def is_mod_name_in_list(mod_name: str) -> bool:
    for info in get_mod_pak_info_list():
        if info['mod_name'] == mod_name:
            return True
    return False


def get_mod_name_dir(mod_name: str) -> dir:
    if is_mod_name_in_list(mod_name):
        return f'{get_uproject_dir()}/Saved/Cooked/{get_unreal_mod_tree_type_str(mod_name)}/{mod_name}'
    return None


def get_mod_name_dir_files(mod_name: str) -> list:
    return get_files_in_tree(get_mod_name_dir(mod_name))


def get_persistant_mod_dir(mod_name: str) -> str:
    return f'{settings.settings_json_dir}/mod_packaging/persistent_files/{mod_name}'


def get_persistant_mod_files(mod_name: str) -> list:
    return get_files_in_tree(get_persistant_mod_dir(mod_name))

# port out
def get_mod_extensions() -> list:
    if general_utils.get_is_game_iostore():
        return [
            'pak',
            'utoc',
            'ucas'
        ]
    else:
        return ['pak']


def get_fix_up_redirectors_before_engine_open() -> bool:
    return settings.settings['engine_info']['resave_packages_and_fix_up_redirectors_before_engine_open']


def get_is_overriding_default_working_dir() -> bool:
    return settings.settings['general_info']['override_default_working_dir']


def get_override_working_dir() -> str:
    return settings.settings['general_info']['working_dir']


def get_working_dir() -> str:
    if get_is_overriding_default_working_dir():
        working_dir = get_override_working_dir()
    else:
        working_dir = f'{settings.SCRIPT_DIR}/working_dir'
    if not os.path.isdir(working_dir):
        os.makedirs(working_dir)
    return working_dir


def clean_working_dir():
    working_dir = get_working_dir()
    if os.path.isdir(working_dir):
        try:
            shutil.rmtree(working_dir)
        except Exception as e:
            log.log_message(f"Error: {e}")

# port out
def get_matching_suffix(path_one: str, path_two: str) -> str:
    common_suffix = []

    for char_one, char_two in zip(path_one[::-1], path_two[::-1]):
        if char_one == char_two:
            common_suffix.append(char_one)
        else:
            break

    return ''.join(common_suffix)[::-1]


def get_clear_uproject_saved_cooked_dir_before_tests() -> bool:
    return settings.settings['engine_info']['clear_uproject_saved_cooked_dir_before_tests']


def get_skip_launching_game() -> bool:
    return settings.settings['game_info']['skip_launching_game']


def get_auto_move_windows() -> dict:
    return settings.settings['auto_move_windows']

# port out
def get_build_target_file_path() -> str:
    return f'{get_uproject_dir()}/Binaries/Win64/{get_uproject_name()}.target'

# port out
def has_build_target_been_built() -> bool:
    return os.path.exists(get_build_target_file_path())


def get_always_build_project() -> str:
    return settings.settings['engine_info']['always_build_project']


def get_engine_cook_and_packaging_args() -> list:
    return settings.settings['engine_info']['engine_cook_and_packaging_args']

# port out
def get_repak_version_str_from_engine_version() -> str:
    engine_version_to_repack_version = {
        "4.0": "V1",
        "4.1": "V1",
        "4.2": "V1",
        "4.3": "V3",
        "4.4": "V3",
        "4.5": "V3",
        "4.6": "V3",
        "4.7": "V3",
        "4.8": "V3",
        "4.9": "V3",
        "4.10": "V3",
        "4.11": "V3",
        "4.12": "V3",
        "4.13": "V3",
        "4.14": "V3",
        "4.15": "V3",
        "4.16": "V4",
        "4.17": "V4",
        "4.18": "V4",
        "4.19": "V4",
        "4.20": "V5",
        "4.21": "V7",
        "4.22": "V8A",
        "4.23": "V8B",
        "4.24": "V8B",
        "4.25": "V9",
        "4.26": "V11",
        "4.27": "V11",
        "4.28": "V11",
        "5.0": "V11",
        "5.1": "V11",
        "5.2": "V11",
        "5.3": "V11",
        "5.4": "V11"
    }
    return engine_version_to_repack_version[custom_get_unreal_engine_version(get_unreal_engine_dir())]


def get_is_overriding_automatic_version_finding() -> bool:
    return settings.settings['repak_info']['override_automatic_version_finding']

# port out
def get_repak_pak_version_str() -> str:
    if get_is_overriding_automatic_version_finding():
        repak_version_str = settings.settings['repak_info']['repak_version']
    else:
        repak_version_str = get_repak_version_str_from_engine_version()
    return repak_version_str

# port out
def get_repak_exe_path() -> str:
    repak_path = settings.settings['repak_info']['repak_path']
    general_utils.check_file_exists(repak_path)
    return repak_path


def get_override_automatic_window_title_finding() -> bool:
    return settings.settings['game_info']['override_automatic_window_title_finding']


def get_window_title_override_string() -> str:
    return settings.settings['game_info']['window_title_override_string']

# port out
def get_game_window_title() -> str:
    if get_override_automatic_window_title_finding():
        return get_window_title_override_string()
    else:
        return os.path.splitext(get_game_process_name())[0]


def filter_file_paths(paths_dict: dict) -> dict:
    filtered_dict = {}
    path_dict_keys = paths_dict.keys()
    for path_dict_key in path_dict_keys:
        if os.path.isfile(path_dict_key):
            filtered_dict[path_dict_key] = paths_dict[path_dict_key]
    return filtered_dict