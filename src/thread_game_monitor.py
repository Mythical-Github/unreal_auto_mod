import threading
import time

import script_states
import utilities
from python_window_management import windows
from enums import ScriptStateType
from python_logging import log
from general_python_utilities import general_utils


found_process = False
found_window = False
window_closed = False
run_monitoring_thread = False
game_monitor_thread = ''


def game_monitor_thread_runner(tick_rate: float = 0.01):
    while run_monitoring_thread:
        time.sleep(tick_rate)
        game_monitor_thread_logic()


def get_game_window():
    return windows.get_window_by_title(utilities.get_game_window_title())


def game_monitor_thread_logic():
    global found_process
    global found_window
    global window_closed

    if not found_process:
        if general_utils.is_process_running(utilities.get_game_process_name()):
            log.log_message('Process: Found Game Process')
            found_process = True
    elif not found_window:
        if get_game_window():
            log.log_message('Window: Game Window Found')
            found_window = True
            script_states.ScriptState.set_script_state(ScriptStateType.POST_GAME_LAUNCH)
    elif not window_closed:
        if not get_game_window():
            log.log_message('Window: Game Window Closed')
            script_states.ScriptState.set_script_state(ScriptStateType.POST_GAME_CLOSE)
            stop_game_monitor_thread()
            window_closed = True


def start_game_monitor_thread():
    global game_monitor_thread
    global run_monitoring_thread
    run_monitoring_thread = True
    game_monitor_thread = threading.Thread(target=game_monitor_thread_runner, daemon=True)
    game_monitor_thread.start()


def stop_game_monitor_thread():
    global run_monitoring_thread
    run_monitoring_thread = False


def game_monitor_thread():
    start_game_monitor_thread()
    log.log_message('Thread: Game Monitoring Thread Started')
    game_monitor_thread.join()
    log.log_message('Thread: Game Monitoring Thread Ended')
