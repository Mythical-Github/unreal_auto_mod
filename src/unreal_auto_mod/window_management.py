import sys

import pywinctl
import screeninfo

from unreal_auto_mod import logger


def does_window_exist(window_title: str, *, use_substring_check: bool = False) -> bool:
    try:
        if use_substring_check:
            all_window_titles = pywinctl.getAllTitles()
            matched_windows = [
                window for window in all_window_titles if window_title in window
            ]
        else:
            all_window_titles = pywinctl.getAllTitles()
            matched_windows = [
                window for window in all_window_titles if window_title == window
            ]
        return len(matched_windows) > 0
    except RuntimeError as e:
        logger.log_message(f"Error: An error occurred: {e}")
        return False


def get_windows_by_title(
    window_title: str, *, use_substring_check: bool = False
) -> list:
    matched_windows = []
    all_windows = pywinctl.getAllWindows()

    if use_substring_check:
        try:
            matched_windows = [
                window for window in all_windows if window_title in window.title
            ]
        except (AttributeError, TypeError) as error_message:
            logger.log_message(
                f"Error processing windows in substring check: {error_message}"
            )
    else:
        try:
            for window in all_windows:
                if str(window.title).strip() == window_title.strip():
                    matched_windows.append(window)
        except (AttributeError, TypeError) as error_message:
            logger.log_message(
                f"Error processing windows in exact match: {error_message}"
            )

    return matched_windows


def get_window_by_title(
    *, window_title: str, use_substring_check: bool = False
) -> pywinctl.Window | None:
    windows = get_windows_by_title(
        window_title=window_title, use_substring_check=use_substring_check
    )
    if not windows:
        logger.log_message(f'Warning: No windows found with title "{window_title}"')
        return None
    return windows[0]


def minimize_window(window: pywinctl.Window):
    pywinctl.Window.minimize(window)


def maximize_window(window: pywinctl.Window):
    pywinctl.Window.maximize(window)


def close_window(window: pywinctl.Window):
    pywinctl.Window.close(window)


def move_window_to_monitor(window: pywinctl.Window, monitor_index: int = 0):
    screen_info = screeninfo.get_monitors()
    if monitor_index < len(screen_info):
        monitor = screen_info[monitor_index]
        window.moveTo(monitor.x, monitor.y)
    else:
        logger.log_message("Monitor: Invalid monitor index.")


def set_window_size(window: pywinctl.Window, width: int, height: int):
    window.size = (width, height)


def change_window_name(window_name: str):
    sys.stdout.write(f"\033]0;{window_name}\007")
    sys.stdout.flush()


def move_window(window: pywinctl.Window, window_settings: dict):
    monitor_index = window_settings["monitor"]
    if monitor_index is not None:
        move_window_to_monitor(window, monitor_index)
    width = window_settings["resolution"]["x"]
    height = window_settings["resolution"]["y"]
    if width is not None:
        set_window_size(window, width, height)
