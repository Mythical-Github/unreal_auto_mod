from unreal_auto_mod import app_runner, hook_states, logger, settings, timer
from unreal_auto_mod.data_structures import ExecutionMode, GameLaunchType, HookStateType
from unreal_auto_mod.programs.steam import get_steam_exe_location


def run_game_exe():
    app_runner.run_app(
        exe_path=settings.get_game_exe_path(),
        exec_mode=ExecutionMode.ASYNC,
        args=settings.get_game_launch_params(),
    )


def run_game_steam():
    if settings.get_override_automatic_launcher_exe_finding():
        steam_exe = settings.get_game_launcher_exe_path()
    else:
        steam_exe = get_steam_exe_location()
    launch_params = []
    launch_params.append("-applaunch")
    launch_params.append(settings.get_game_id())
    new_params = settings.get_game_launch_params()
    for param in new_params:
        launch_params.append(param)
    app_runner.run_app(
        exe_path=steam_exe, exec_mode=ExecutionMode.ASYNC, args=launch_params
    )


@hook_states.hook_state_decorator(HookStateType.PRE_GAME_LAUNCH)
def run_game():
    logger.log_message(
        f"Timer: Time since script execution: {timer.get_running_time()}"
    )
    launch_type = GameLaunchType(settings.get_game_info_launch_type_enum_str_value())
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
        unsupported_launch_type_error = (
            "Unsupported launch_type specified in the settings.json"
        )
        raise ValueError(unsupported_launch_type_error)
