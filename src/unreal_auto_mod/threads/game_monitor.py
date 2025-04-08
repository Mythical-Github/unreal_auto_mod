import threading
import time
from dataclasses import dataclass

import unreal_auto_mod.timer
from unreal_auto_mod import (
    hook_states,
    logger,
    process_management,
    utilities,
    window_management,
)
from unreal_auto_mod.data_structures import HookStateType


@dataclass
class GameMonitorThreadInformation:
    init_done: bool
    found_window: bool
    found_process: bool
    window_closed: bool
    run_game_monitor_thread: bool
    game_monitor_thread: threading.Thread


game_monitor_thread_information = GameMonitorThreadInformation(
    init_done=False,
    found_window=False,
    found_process=False,
    window_closed=False,
    run_game_monitor_thread=False,
    game_monitor_thread=None,  # type: ignore
)


def game_monitor_thread_runner(tick_rate: float = 0.01):
    while game_monitor_thread_information.run_game_monitor_thread:
        time.sleep(tick_rate)
        game_monitor_thread_logic()


def get_game_window():
    return window_management.get_window_by_title(
        window_title=utilities.get_game_window_title()
    )


@hook_states.hook_state_decorator(HookStateType.POST_GAME_LAUNCH)
def found_game_window():
    logger.log_message("Window: Game Window Found")
    game_monitor_thread_information.found_window = True


def game_monitor_thread_logic():
    if (
        not game_monitor_thread_information.found_process
        and process_management.is_process_running(
            process_management.get_game_process_name()
        )
    ):
        logger.log_message("Process: Found Game Process")
        game_monitor_thread_information.found_process = True

    elif not game_monitor_thread_information.found_window:
        time.sleep(4)
        if get_game_window():
            found_game_window()

    elif not game_monitor_thread_information.window_closed and not get_game_window():
        logger.log_message("Window: Game Window Closed")
        stop_game_monitor_thread()
        game_monitor_thread_information.window_closed = True


def start_game_monitor_thread():
    game_monitor_thread_information.run_game_monitor_thread = True
    game_monitor_thread_information.game_monitor_thread = threading.Thread(
        target=game_monitor_thread_runner, daemon=True
    )
    game_monitor_thread_information.game_monitor_thread.start()


@hook_states.hook_state_decorator(HookStateType.POST_GAME_CLOSE)
def stop_game_monitor_thread():
    game_monitor_thread_information.run_game_monitor_thread = False


def game_monitor_thread():
    start_game_monitor_thread()
    logger.log_message("Thread: Game Monitoring Thread Started")
    game_monitor_thread_information.game_monitor_thread.join()
    logger.log_message("Thread: Game Monitoring Thread Ended")
    logger.log_message(
        f"Timer: Time since script execution: {unreal_auto_mod.timer.get_running_time()}"
    )
