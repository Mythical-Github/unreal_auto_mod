import os
import winreg

from unreal_auto_mod import log_py as log
from unreal_auto_mod import script_states, utilities
from unreal_auto_mod.enums import ExecutionMode, GameLaunchType, ScriptStateType


def get_steam_exe_location():
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", 0, winreg.KEY_READ)
        install_path, _ = winreg.QueryValueEx(reg_key, "InstallPath")
        winreg.CloseKey(reg_key)
        steam_exe_path = os.path.join(install_path, 'steam.exe')
        return steam_exe_path
    except FileNotFoundError:
        return "Steam: installation not found in the registry."
    except Exception as e:
        return f"Error: An error occurred: {e}"


def get_epic_launcher_exe_location():
    first_arg = winreg.HKEY_LOCAL_MACHINE
    second_arg = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    reg_key = winreg.OpenKey(first_arg, second_arg, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
    for i in range(winreg.QueryInfoKey(reg_key)[0]):
        sub_key_name = winreg.EnumKey(reg_key, i)
        sub_key = winreg.OpenKey(reg_key, sub_key_name)
        try:
            display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
            if "Epic Games Launcher" in display_name:
                install_path, _ = winreg.QueryValueEx(sub_key, "InstallLocation")
                epic_launcher_exe_path = os.path.join(install_path, 'Portal', 'Binaries', 'Win32', 'EpicGamesLauncher.exe')
                return epic_launcher_exe_path
        except FileNotFoundError:
            pass
        finally:
            winreg.CloseKey(sub_key)
    winreg.CloseKey(reg_key)
    return "Epic Games Launcher installation not found in the registry."


def run_game_exe():
    utilities.run_app(exe_path=utilities.get_game_exe_path(), exec_mode=ExecutionMode.ASYNC, args=utilities.get_game_launch_params())


def run_game_steam():
    if utilities.get_override_automatic_launcher_exe_finding():
        steam_exe = utilities.get_game_launcher_exe_path()
    else:
        steam_exe = get_steam_exe_location()
    launch_params = []
    launch_params.append('-applaunch')
    launch_params.append(utilities.get_game_id())
    new_params = utilities.get_game_launch_params()
    for param in new_params:
        launch_params.append(param)
    utilities.run_app(exe_path=steam_exe, exec_mode=ExecutionMode.ASYNC, args=launch_params)


def run_game():
    log.log_message(f'Timer: Time since script execution: {utilities.get_running_time()}')
    script_states.ScriptState.set_script_state(ScriptStateType.PRE_GAME_LAUNCH)
    launch_type = GameLaunchType(utilities.get_game_info_launch_type_enum_str_value())
    if launch_type == GameLaunchType.EXE:
        run_game_exe()
    elif launch_type == GameLaunchType.STEAM:
        run_game_steam()
    # elif launch_type == game_launch_type.EPIC:
    #     pass
    # elif launch_type == game_launch_type.ITCH_IO:
    #     pass
    # elif launch_type == game_launch_type.BATTLE_NET:
    #     pass
    # elif launch_type == game_launch_type.ORIGIN:
    #     pass
    # elif launch_type == game_launch_type.UBISOFT:
    #     pass
    else:
        raise ValueError('Unsupported launch_type specified in the settings.json')
