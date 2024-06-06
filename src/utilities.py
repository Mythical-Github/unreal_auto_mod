import os
import glob
import json
import shutil
import hashlib
import subprocess
import psutil
import settings
from enums import PackagingDirType, ExecutionMode, ScriptStateType, CompressionType, get_enum_from_val


def check_file_exists(file_path: str) -> bool:
    if os.path.exists(file_path):
        return True
    else:
        raise FileNotFoundError(f'Settings file "{file_path}" not found.')


# def check_file_exists(file_path: str) -> bool:
#     return os.path.exists(file_path)


def get_process_name(exe_path: str) -> str:
    filename = os.path.basename(exe_path)
    return filename


def get_game_process_name() -> str:
    process = settings.settings['game_info']['game_exe_path']
    return get_process_name(process)


def kill_process(process_name: str):
    if is_process_running(process_name):
        os.system(f'taskkill /f /im {process_name}')


def is_process_running(process_name: str) -> bool:
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def get_processes_by_substring(substring: str) -> list:
    all_processes = psutil.process_iter(['pid', 'name'])
    matching_processes = [proc.info for proc in all_processes if substring.lower() in proc.info['name'].lower()]
    return matching_processes


def kill_processes(state: ScriptStateType):
    process_to_kill_info = settings.settings['process_kill_info']['processes']
    current_state = state.value if isinstance(state, ScriptStateType) else state

    for process_info in process_to_kill_info:
        target_state = process_info.get('script_state')
        if target_state == current_state:
            if process_info['use_substring_check']:
                proc_name_substring = process_info['process_name']
                matching_processes = get_processes_by_substring(proc_name_substring)
                for proc_info in matching_processes:
                    proc_name = proc_info['name']
                    kill_process(proc_name)
            else:
                proc_name = process_info['process_name']
                kill_process(proc_name)


def get_unreal_engine_version(engine_path: str) -> str:
    if settings.settings['engine_info']['override_automatic_version_finding']:
        unreal_engine_major_version = settings.settings['engine_info']['unreal_engine_major_version']
        unreal_engine_minor_version = settings.settings['engine_info']['unreal_engine_minor_version']
        return f'{unreal_engine_major_version}.{unreal_engine_minor_version}'
    else:
        version_file_path = f'{engine_path}/Engine/Build/Build.version'        
        check_file_exists(version_file_path)
        with open(version_file_path, 'r') as f:
            version_info = json.load(f)
            unreal_engine_major_version = version_info.get('MajorVersion', 0)
            unreal_engine_minor_version = version_info.get('MinorVersion', 0)
            return f'{unreal_engine_major_version}.{unreal_engine_minor_version}'


def get_is_game_iostore() -> bool:
    is_game_iostore = False
    file_extensions = get_file_extensions(get_game_paks_dir())
    for file_extension in file_extensions:
        if file_extension == '.ucas':
            is_game_iostore = True
        elif file_extension == '.utoc':
            is_game_iostore = True
    return is_game_iostore


def get_game_paks_dir() -> str:
    game_exe_path = settings.settings['game_info']['game_exe_path']
    game_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(game_exe_path)))))
    uproject = settings.settings['engine_info']['unreal_project_file']
    uproject_name = os.path.basename(uproject)[:-9]
    if settings.settings['alt_uproject_name_in_game_dir']['use_alt_method']:
        alt_dir_name = settings.settings['alt_uproject_name_in_game_dir']['name']
        _dir = f'{game_dir}/{alt_dir_name}/Content/Paks'
    else:
        _dir = f'{game_dir}/{uproject_name}/Content/Paks'
    return _dir


def get_win_dir_type() -> PackagingDirType:
    engine_dir = settings.settings['engine_info']['unreal_engine_dir']
    ue_version = get_unreal_engine_version(engine_dir)
    if ue_version.startswith('5'):
        return PackagingDirType.WINDOWS
    else:
        return PackagingDirType.WINDOWS_NO_EDITOR


def is_game_ue5() -> bool:
    return get_win_dir_type() == PackagingDirType.WINDOWS


def is_game_ue4() -> bool:
    return get_win_dir_type() == PackagingDirType.WINDOWS_NO_EDITOR


def get_file_hash(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hashlib.md5().update(chunk)
    return hashlib.md5().hexdigest()


def get_do_files_have_same_hash(file_path_one: str, file_path_two: str) -> bool:
    if os.path.exists(file_path_one) and os.path.exists(file_path_two):
        hash_one = get_file_hash(file_path_one)
        hash_two = get_file_hash(file_path_two)
        return hash_one == hash_two
    else:
        return None


def get_unreal_engine_dir() -> str:
    return settings.settings['engine_info']['unreal_engine_dir']


def get_unreal_editor_exe_path() -> str:
    engine_dir = settings.settings['engine_info']['unreal_engine_dir']
    test = get_win_dir_type()
    if test == PackagingDirType.WINDOWS_NO_EDITOR:
        engine_path_suffix = '/Engine/Binaries/Win64/UE4Editor.exe'
    else:
        engine_path_suffix = '/Engine/Binaries/Win64/UnrealEditor.exe'
    engine_exe = f'{engine_dir}{engine_path_suffix}'
    return engine_exe


def is_toggle_engine_during_testing_in_use() -> bool:
    return settings.settings['engine_info']['toggle_engine_during_testing']


def run_app(exe_path: str, exec_mode: ExecutionMode, args: str = {}, working_dir: str = None):
    command = exe_path
    for arg in args:
        command = f'{command} {arg}'
    print(f'{command} was ran with {exec_mode} enum')
    if exec_mode == ExecutionMode.SYNC:
        subprocess.run(command, cwd=working_dir)
    elif exec_mode == ExecutionMode.ASYNC:
        subprocess.Popen(command, cwd=working_dir, start_new_session=True)
    

def get_engine_window_title() -> str:
    uproject_path = settings.settings['engine_info']['unreal_project_file']
    proc_name_prefix = get_process_name(uproject_path)[:-9]
    proc_name_suffix = 'Unreal Editor'
    engine_proc_name = f'{proc_name_prefix} - {proc_name_suffix}'
    return engine_proc_name


def get_engine_process_name() -> str:
    exe_path = get_unreal_editor_exe_path()
    return get_process_name(exe_path)


def get_files_in_tree(tree_path: str) -> list:
    return glob.glob(tree_path + '/**/*', recursive=True)


def get_file_extension(file_path: str) -> str:
    _, file_extension = os.path.splitext(file_path)
    return file_extension


def get_file_extensions(file_path: str) -> list:
    extensions = []
    files = get_files_in_tree(file_path)
    for file in files:
        extensions.append(get_file_extension(file))
    return extensions


def get_game_content_dir():
    return os.path.dirname(get_game_paks_dir())


def get_game_dir():
    return os.path.dirname(get_game_content_dir())


def get_uproject_file() -> str:
    return settings.settings['engine_info']['unreal_project_file']


def get_uproject_name() -> str:
    return os.path.splitext(os.path.basename(get_uproject_file()))[0]


def get_uproject_dir() -> str:
    return os.path.dirname(get_uproject_file())


def get_win_dir_str() -> str:
    win_dir_type = 'Windows'
    if is_game_ue4():
        win_dir_type = f'{win_dir_type}NoEditor'
    return win_dir_type


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


def get_mod_pak_info(mod_name:str) -> dict:
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
        return f'{get_uproject_dir}/Saved/Cooked/{get_unreal_mod_tree_type_str(mod_name)}/{mod_name}'
    return None


def get_mod_name_dir_files(mod_name: str) -> list:
    return get_files_in_tree(get_mod_name_dir(mod_name))


def get_persistant_mod_dir(mod_name: str) -> str:
    prefix = f'{settings.SCRIPT_DIR}/presets/{settings.GAME_NAME}'
    suffix = f'{settings.PRESET_NAME}/mod_packaging/persistent_files/{mod_name}'
    return f'{prefix}/{suffix}'


def get_persistant_mod_files(mod_name: str) -> list:
    return get_files_in_tree(get_persistant_mod_dir(mod_name))
 

def get_mod_extensions() -> list:
    if get_is_game_iostore():
        return [
            'pak',
            'utoc',
            'ucas'
        ]
    else:
        return ['pak']


def get_fix_up_redirectors_before_engine_open() -> bool:
    return settings.settings['engine_info']['resave_packages_and_fix_up_redirectors_before_engine_open']


def get_working_dir() -> str:
    if settings.settings['general_info']['override_default_working_dir']:
        working_dir = settings.settings['general_info']['working_dir']
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
            print(f"Error: {e}")


def get_matching_suffix(path_one: str, path_two: str) -> str:
    rev_one = path_one[::-1]
    rev_two = path_two[::-1]
    common_suffix = []

    for char_one, char_two in zip(rev_one, rev_two):
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


def has_build_target_been_built() -> bool:
    build_target_file = f'{get_uproject_dir()}/Binaries/Win64/{get_uproject_name()}.target'
    return os.path.exists(build_target_file)


def get_always_build_project() -> str:
    return settings.settings['engine_info']['always_build_project']


def get_engine_cook_and_packaging_args() -> list:
    return settings.settings['engine_info']['engine_cook_and_packaging_args']


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
    return engine_version_to_repack_version[get_unreal_engine_version(get_unreal_engine_dir())]


def get_is_overriding_automatic_version_finding() -> bool:
    return settings.settings['repak_info']['override_automatic_version_finding']


def get_repak_pak_version_str() -> str:
    if get_is_overriding_automatic_version_finding():
        repak_version_str = settings.settings['repak_info']['repak_version']
    else:
        repak_version_str = get_repak_version_str_from_engine_version()
    return repak_version_str


def get_repak_exe_path() -> str:
    return settings.settings['repak_info']['repak_path']


def get_override_automatic_window_title_finding() -> bool:
    return settings.settings['game_info']['override_automatic_window_title_finding']


def get_window_title_override_string() -> str:
    return settings.settings['game_info']['window_title_override_string']


def get_game_window_title() -> str:
    if get_override_automatic_window_title_finding():
        return get_window_title_override_string()
    else:
        return os.path.splitext(get_game_process_name())[0]
