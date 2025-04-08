from unreal_auto_mod import log_py as log
from unreal_auto_mod import settings, utilities, win_man_enums, win_man_py
from unreal_auto_mod import win_man_py as windows
from unreal_auto_mod.enums import ExecutionMode, ScriptStateType, get_enum_from_val


def alt_exe_checks(script_state_type: ScriptStateType):
    alt_exe_methods = utilities.get_alt_exe_methods()
    for alt_exe_method in alt_exe_methods:
        value = alt_exe_method['script_state']
        exe_state = get_enum_from_val(ScriptStateType, value)
        if exe_state == script_state_type:
            exe_path = alt_exe_method['alt_exe_path']
            exe_args = alt_exe_method['variable_args']
            exe_exec_mode = get_enum_from_val(ExecutionMode, alt_exe_method['execution_mode'])
            utilities.run_app(exe_path, exe_exec_mode, exe_args)


def is_script_state_used(state: ScriptStateType) -> bool:
    if isinstance(settings.settings, dict):
        if "process_kill_info" in settings.settings:
            process_kill_info = settings.settings.get("process_kill_info", {})
            if "processes" in process_kill_info:
                for process in process_kill_info["processes"]:
                    if isinstance(state, ScriptStateType):
                        state = state.value
                    if process.get("script_state") == state:
                        return True

        if "auto_move_windows" in settings.settings:
            for window in utilities.get_auto_move_windows():
                if isinstance(state, ScriptStateType):
                    state = state.value
                if window.get("script_state") == state:
                    return True

        if "alt_exe_methods" in settings.settings:
            for method in utilities.get_alt_exe_methods():
                if isinstance(state, ScriptStateType):
                    state = state.value
                if method.get("script_state") == state:
                    return True

    return False


def window_checks(current_state: win_man_enums.WindowAction):
    window_settings_list = utilities.get_auto_move_windows()
    for window_settings in window_settings_list:
        settings_state = get_enum_from_val(ScriptStateType, window_settings['script_state'])
        if settings_state == current_state:
            title = window_settings['window_name']
            windows_to_change = win_man_py.get_windows_by_title(title)
            for window_to_change in windows_to_change:
                way_to_change_window = get_enum_from_val(win_man_enums.WindowAction, window_settings['window_behaviour'])
                if way_to_change_window == win_man_enums.WindowAction.MAX:
                    windows.maximize_window(window_to_change)
                elif way_to_change_window == win_man_enums.WindowAction.MIN:
                    windows.minimize_window(window_to_change)
                elif way_to_change_window == win_man_enums.WindowAction.CLOSE:
                    windows.close_window(window_to_change)
                elif way_to_change_window == win_man_enums.WindowAction.MOVE:
                    windows.move_window(window_to_change, window_settings)
                else:
                    log.log_message('Monitor: invalid window behavior specified in settings')


def routine_checks(state: ScriptStateType):
    if state != ScriptStateType.CONSTANT:
        log.log_message(f'Routine Check: {state} is running')
    if is_script_state_used(state):
        utilities.kill_processes(state)
        window_checks(state)
        alt_exe_checks(state)
    if state != ScriptStateType.CONSTANT:
        log.log_message(f'Routine Check: {state} finished')


class ScriptState:
    global script_state

    def set_script_state(new_state: ScriptStateType):
        global script_state
        script_state = new_state
        log.log_message(f'Script State: changed to {new_state}')
        # calling this on preinit causes problems so will avoid for now
        if new_state != ScriptStateType.PRE_INIT:
            routine_checks(new_state)
            routine_checks(ScriptStateType.PRE_ALL)
            routine_checks(ScriptStateType.POST_ALL)
            log.log_message(f'Timer: Time since script execution: {utilities.get_running_time()}')
