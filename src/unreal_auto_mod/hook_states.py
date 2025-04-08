from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from unreal_auto_mod import (
    app_runner,
    logger,
    process_management,
    settings,
    timer,
    window_management,
)
from unreal_auto_mod.data_structures import (
    ExecutionMode,
    HookStateType,
    WindowAction,
    get_enum_from_val,
)


@dataclass
class HookStateInfo:
    hook_state: HookStateType


hook_state_info = HookStateInfo(HookStateType.PRE_INIT)


def exec_events_checks(hook_state_type: HookStateType):
    exec_events = settings.get_exec_events()
    for exec_event in exec_events:
        value = exec_event["hook_state"]
        exe_state = get_enum_from_val(HookStateType, value)
        if exe_state == hook_state_type:
            exe_path = exec_event["alt_exe_path"]
            exe_args = exec_event["variable_args"]
            exe_exec_mode = get_enum_from_val(
                ExecutionMode, exec_event["execution_mode"]
            )
            if not exe_exec_mode:
                app_runner.run_app(exe_path, exe_exec_mode, exe_args)
            else:
                exe_exec_error = "exe_exec_mode returned none"
                raise RuntimeError(exe_exec_error)


def is_hook_state_used(state: HookStateType) -> bool:
    if isinstance(settings.settings_information.settings, dict):
        if "process_kill_events" in settings.settings_information.settings:
            process_kill_events = settings.settings_information.settings.get(
                "process_kill_events", {}
            )
            if "processes" in process_kill_events:
                for process in process_kill_events["processes"]:
                    if process.get("hook_state") == state:
                        return True

        if "window_management_events" in settings.settings_information.settings:
            for window in settings.get_window_management_events():
                if window.get("hook_state") == state:
                    return True

        if "exec_events" in settings.settings_information.settings:
            for method in settings.get_exec_events():
                if method.get("hook_state") == state:
                    return True

    return False


def window_checks(current_state: HookStateType):
    window_settings_list = settings.get_window_management_events()
    for window_settings in window_settings_list:
        settings_state = get_enum_from_val(HookStateType, window_settings["hook_state"])
        if settings_state == current_state:
            title = window_settings["window_name"]
            windows_to_change = window_management.get_windows_by_title(
                title, use_substring_check=window_settings["use_substring_check"]
            )
            for window_to_change in windows_to_change:
                way_to_change_window = get_enum_from_val(
                    WindowAction, window_settings["window_behaviour"]
                )
                if way_to_change_window == WindowAction.MAX:
                    window_management.maximize_window(window_to_change)
                elif way_to_change_window == WindowAction.MIN:
                    window_management.minimize_window(window_to_change)
                elif way_to_change_window == WindowAction.CLOSE:
                    window_management.close_window(window_to_change)
                elif way_to_change_window == WindowAction.MOVE:
                    window_management.move_window(window_to_change, window_settings)
                else:
                    logger.log_message(
                        "Monitor: invalid window behavior specified in settings"
                    )


def hook_state_checks(hook_state: HookStateType):
    if hook_state != HookStateType.CONSTANT:
        logger.log_message(f"Hook State Check: {hook_state} is running")
    if is_hook_state_used(hook_state):
        process_management.kill_processes(hook_state)
        window_checks(hook_state)
        exec_events_checks(hook_state)
    if hook_state != HookStateType.CONSTANT:
        logger.log_message(f"Hook State Check: {hook_state} finished")


def set_hook_state(new_state: HookStateType):
    hook_state_info.hook_state = new_state
    logger.log_message(f"Hook State: changed to {new_state}")
    # calling this on preinit causes problems so will avoid for now
    if new_state != HookStateType.PRE_INIT:
        hook_state_checks(HookStateType.PRE_ALL)
        hook_state_checks(new_state)
        hook_state_checks(HookStateType.POST_ALL)
        logger.log_message(
            f"Timer: Time since script execution: {timer.get_running_time()}"
        )


def hook_state_decorator(
    start_hook_state_type: HookStateType,
    end_hook_state_type: HookStateType | None = None,
):
    def decorator(function: Callable[..., Any]):
        def wrapper(*args, **kwargs):
            set_hook_state(start_hook_state_type)
            result = function(*args, **kwargs)
            if end_hook_state_type is not None:
                set_hook_state(end_hook_state_type)
            return result

        return wrapper

    return decorator
