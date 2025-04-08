import threading
import time

from unreal_auto_mod import gen_py_utils as general_utils
from unreal_auto_mod import log_py as log
from unreal_auto_mod import script_states, utilities, win_man_py
from unreal_auto_mod import ue_dev_py_utils as unreal_dev_utils
from unreal_auto_mod.enums import ScriptStateType

init_done = False


def engine_monitor_thread():
    # later on have this only activate when
    start_engine_monitor_thread()
    log.log_message('Thread: Engine Monitoring Thread Started')
    engine_monitor_thread.join()
    log.log_message('Thread: Engine Monitoring Thread Ended')


def engine_monitor_thread_runner(tick_rate: float = 0.01):
    while run_monitoring_thread:
        time.sleep(tick_rate)
        engine_monitor_thread_logic()


def engine_monitor_thread_logic():
    global found_process
    global found_window
    global window_closed
    global init_done

    if not init_done:
        found_process = False
        found_window = False
        window_closed = False
        init_done = True

    engine_window_name = unreal_dev_utils.get_engine_window_title(utilities.get_uproject_file())
    if not found_process:
        engine_process_name = unreal_dev_utils.get_engine_process_name(utilities.get_unreal_engine_dir())
        if general_utils.is_process_running(engine_process_name):
            log.log_message('Process: Found Engine Process')
            found_process = True
    elif not found_window:
        if win_man_py.win_man_py.does_window_exist(engine_window_name):
            log.log_message('Window: Engine Window Found')
            found_window = True
            script_states.ScriptState.set_script_state(ScriptStateType.POST_ENGINE_OPEN)
    elif not window_closed:
        if not win_man_py.win_man_py.does_window_exist(engine_window_name):
            log.log_message('Window: Engine Window Closed')
            window_closed = True
            script_states.ScriptState.set_script_state(ScriptStateType.POST_ENGINE_CLOSE)
            stop_engine_monitor_thread()


def start_engine_monitor_thread():
    global engine_monitor_thread
    global run_monitoring_thread
    run_monitoring_thread = True
    engine_monitor_thread = threading.Thread(target=engine_monitor_thread_runner, daemon=True)
    engine_monitor_thread.start()


def stop_engine_monitor_thread():
    global run_monitoring_thread
    run_monitoring_thread = False
