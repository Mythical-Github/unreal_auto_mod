import os
import sys
import time

import psutil
import pyjson5 as json

import unreal_auto_mod.gen_py_utils as gen_utils
from unreal_auto_mod import mods

start_time = time.time()

settings = ''
init_settings_done = False
settings_json_dir = ''
program_dir = ''
mod_names = []
settings_json = ''


if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
os.chdir(SCRIPT_DIR)


def init_settings(settings_json_path: str):
    global settings
    global init_settings_done
    global settings_json
    global settings_json_dir

    with open(settings_json_path) as file:
        settings = json.load(file)
    window_name = settings['general_info']['window_title']
    os.system(f'title {window_name}')
    auto_close_game = settings['process_kill_info']['auto_close_game']
    if auto_close_game:
        def is_process_running(process_name):
            for proc in psutil.process_iter():
                try:
                    if process_name.lower() in proc.name().lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return False

        process_name = settings['game_info']['game_exe_path']
        process_name = os.path.basename(process_name)
        if is_process_running(process_name):
            os.system(f'taskkill /f /im {process_name}')
    init_settings_done = True
    settings_json = settings_json_path
    settings_json_dir = os.path.dirname(settings_json)


def check_file_exists(file_path: str) -> bool:
    if os.path.exists(file_path):
        return True
    else:
        raise FileNotFoundError(f'File "{file_path}" not found.')


def unreal_engine_check():
    from unreal_auto_mod import log_py as log
    from unreal_auto_mod import ue_dev_py_utils as ue_dev_utils
    from unreal_auto_mod import utilities

    should_do_check = True

    if utilities.get_should_ship_uproject_steps():
        if not utilities.is_unreal_pak_packing_enum_in_use():
               should_do_check = False

    if should_do_check:
        engine_str = 'UE4Editor'
        if ue_dev_utils.is_game_ue5(utilities.get_unreal_engine_dir()):
            engine_str = 'UnrealEditor'
        check_file_exists(f'{utilities.get_unreal_engine_dir()}/Engine/Binaries/Win64/{engine_str}.exe')
        log.log_message('Check: Unreal Engine exists')


def init_checks():
    from unreal_auto_mod import log_py as log
    from unreal_auto_mod import utilities
    if not utilities.get_should_ship_uproject_steps():
        check_file_exists(utilities.get_uproject_file())
        log.log_message('Check: Uproject file exists')

    unreal_engine_check()

    if utilities.get_is_using_repak_path_override():
        check_file_exists(utilities.get_repak_path_override())
        log.log_message('Check: Repak exists')

    if not utilities.get_skip_launching_game():
        check_file_exists(utilities.get_game_exe_path())
        log.log_message('Check: Game exists')

    log.log_message('Check: Passed all init checks')


def load_settings(settings_json: str):
    if not init_settings_done:
        init_settings(settings_json)
    init_checks()
    with open(settings_json) as file:
        return json.load(file)


def save_settings(settings_json: str):
    with open(settings_json, 'w') as file:
        json.dump(settings, file, indent=2)


def pass_settings(settings_json: str):
    load_settings(settings_json)


def test_mods(settings_json: str, input_mod_names: str):
    load_settings(settings_json)
    global mod_names
    for mod_name in input_mod_names:
        mod_names.append(mod_name)
    mods.create_mods()


def test_mods_all(settings_json: str):
    load_settings(settings_json)
    global mod_names
    for entry in settings['mod_pak_info']:
        mod_names.append(entry['mod_name'])
    mods.create_mods()


def open_stove(settings_json: str):
    load_settings(settings_json)
    from unreal_auto_mod import utilities
    if not os.path.isfile(utilities.does_stove_exist()):
        utilities.install_stove()
    utilities.run_app(utilities.get_stove_path(),)


def open_spaghetti(settings_json: str):
    load_settings(settings_json)
    from unreal_auto_mod import utilities
    if not os.path.isfile(utilities.get_spaghetti_path()):
        utilities.install_spaghetti()
    utilities.run_app(utilities.get_spaghetti_path())


def open_kismet_analyzer(settings_json: str):
    load_settings(settings_json)
    from unreal_auto_mod import utilities
    # add shell stuff to run app later or something
    if not os.path.isfile(utilities.get_kismet_analyzer_path()):
        utilities.install_kismet_analyzer()
    import subprocess
    kismet_analyzer_path = utilities.get_kismet_analyzer_path()
    kismet_directory = os.path.dirname(kismet_analyzer_path)
    command = f'cd /d "{kismet_directory}" && "{kismet_analyzer_path}" -h && set ka=kismet-analyzer.exe && cmd /k'
    subprocess.run(command, shell=True, check=False)


def open_uasset_gui(settings_json: str):
    load_settings(settings_json)
    from unreal_auto_mod import utilities
    if not os.path.isfile(utilities.get_uasset_gui_path()):
        utilities.install_uasset_gui()
    utilities.run_app(utilities.get_uasset_gui_path())


def open_latest_log(settings_json: str):
    load_settings(settings_json)
    from unreal_auto_mod import utilities
    file_to_open = f'{utilities.get_uproject_unreal_auto_mod_resources_dir()}/UnrealAutoMod/logs/latest.log'
    gen_utils.open_file_in_default(file_to_open)


def open_settings_json(settings_json: str):
    load_settings(settings_json)
    gen_utils.open_file_in_default(settings.settings_json)


def run_game(settings_json: str):
    load_settings(settings_json)
    from unreal_auto_mod import game_runner, thread_game_monitor
    game_runner.run_game()
    thread_game_monitor.game_monitor_thread()


def open_umodel(settings_json: str):
    load_settings(settings_json)
    from unreal_auto_mod import utilities
    if not os.path.isfile(utilities.does_umodel_exist()):
        utilities.install_umodel()
    # Sets dir, so it's the dir opened by default in umodel
    os.chdir(os.path.dirname(utilities.custom_get_game_dir()))
    utilities.run_app(utilities.get_umodel_path())


def open_fmodel(settings_json: str):
    load_settings(settings_json)
    from unreal_auto_mod import utilities
    if not os.path.isfile(utilities.get_fmodel_path()):
        utilities.install_fmodel()
    utilities.run_app(utilities.get_fmodel_path())
