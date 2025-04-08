from unreal_auto_mod import gen_py_utils as general_utils
from unreal_auto_mod import script_states, thread_engine_monitor, ue_dev_py_enums, ue_dev_py_utils, utilities
from unreal_auto_mod.enums import ExecutionMode, ScriptStateType


def open_game_engine():
    script_states.ScriptState.set_script_state(ScriptStateType.PRE_ENGINE_OPEN)
    command = ue_dev_py_utils.get_unreal_editor_exe_path(utilities.get_unreal_engine_dir())
    utilities.run_app(command, ExecutionMode.ASYNC, utilities.get_engine_launch_args())
    script_states.ScriptState.set_script_state(ScriptStateType.POST_ENGINE_OPEN)


def close_game_engine():
    script_states.ScriptState.set_script_state(ScriptStateType.PRE_ENGINE_CLOSE)
    if ue_dev_py_utils.get_win_dir_type(utilities.get_unreal_engine_dir()) == ue_dev_py_enums.PackagingDirType.WINDOWS_NO_EDITOR:
        game_engine_processes = general_utils.get_processes_by_substring('UE4Editor')
    else:
        game_engine_processes = general_utils.get_processes_by_substring('UnrealEditor')
    for process_info in game_engine_processes:
        general_utils.kill_process(process_info['name'])
    script_states.ScriptState.set_script_state(ScriptStateType.POST_ENGINE_CLOSE)


def fix_up_uproject_redirectors():
    close_game_engine()
    arg = '-run=ResavePackages -fixupredirects'
    command = f'"{ue_dev_py_utils.get_unreal_editor_exe_path(utilities.get_unreal_engine_dir())}" "{utilities.get_uproject_file()}" {arg}'
    utilities.run_app(command)


def toggle_engine_off():
    if utilities.is_toggle_engine_during_testing_in_use():
        close_game_engine()


def toggle_engine_on():
    if utilities.is_toggle_engine_during_testing_in_use():
        if utilities.get_fix_up_redirectors_before_engine_open():
            fix_up_uproject_redirectors()
        open_game_engine()
        thread_engine_monitor.engine_monitor_thread()
