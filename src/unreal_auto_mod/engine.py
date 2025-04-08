from unreal_auto_mod import (
    app_runner,
    hook_states,
    logger,
    process_management,
    settings,
)
from unreal_auto_mod.data_structures import (
    ExecutionMode,
    HookStateType,
    PackagingDirType,
)
from unreal_auto_mod.programs import unreal_engine
from unreal_auto_mod.threads import thread_engine_monitor


@hook_states.hook_state_decorator(HookStateType.PRE_ENGINE_OPEN)
def open_game_engine():
    command = unreal_engine.get_unreal_editor_exe_path(settings.get_unreal_engine_dir())
    app_runner.run_app(command, ExecutionMode.ASYNC, settings.get_engine_launch_args())
    thread_engine_monitor.engine_monitor_thread()


@hook_states.hook_state_decorator(HookStateType.POST_ENGINE_CLOSE)
def post_engine_closed_message():
    logger.log_message("Closed Unreal Engine.")


@hook_states.hook_state_decorator(HookStateType.PRE_ENGINE_CLOSE)
def close_game_engine():
    if (
        unreal_engine.get_win_dir_type(settings.get_unreal_engine_dir())
        == PackagingDirType.WINDOWS_NO_EDITOR
    ):
        game_engine_processes = process_management.get_processes_by_substring(
            "UE4Editor"
        )
    else:
        game_engine_processes = process_management.get_processes_by_substring(
            "UnrealEditor"
        )
    for process_info in game_engine_processes:
        process_management.kill_process(process_info["name"])
    post_engine_closed_message()


def toggle_engine_off():
    close_game_engine()


def toggle_engine_on():
    open_game_engine()
