from os import system
from screeninfo import get_monitors
from utilities import get_game_process_name
from enums import WindowAction, ScriptStateType, get_enum_from_val
from pygetwindow import getAllTitles, getWindowsWithTitle, getAllWindows, Win32Window, Window


def does_window_exist(window_title: str, use_substring_check: bool = False) -> bool:
    try:
        if use_substring_check:
            all_window_titles = getAllTitles()
            matched_windows = [window for window in all_window_titles if window_title in window]
            return len(matched_windows) > 0
        else:
            all_window_titles = getWindowsWithTitle(window_title)
            return len(all_window_titles) > 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def get_windows_by_title(window_title: str, use_substring_check: bool = False) -> list:
    if use_substring_check:
        all_windows = getAllWindows()
        matched_windows = [window for window in all_windows if window_title in window.title]
        return matched_windows
    else:
        matched_windows = getWindowsWithTitle(window_title)
        return matched_windows


def get_window_by_title(window_title: str, use_substring_check: bool = False) -> Win32Window:
    windows = get_windows_by_title(window_title, use_substring_check)
    if not windows:
        raise ValueError(f'No windows found with title "{window_title}"')
    return windows[0]


def minimize_window(window: Win32Window):
    Window.minimize(window)


def maximize_window(window: Win32Window):
    Window.maximize(window)


def close_window(window: Win32Window):
    Window.close(window)


def move_window_to_monitor(window: Win32Window, monitor_index: int = 0):
    screen_info = get_monitors()
    if monitor_index < len(screen_info):
        monitor = screen_info[monitor_index]
        window.moveTo(monitor.x, monitor.y)
    else:
        print('Invalid monitor index.')


def set_window_size(window: Win32Window, width: int, height: int):
    window.size = (width, height)


def change_window_name(window_name: str):
    system(f'title {window_name}')


def get_game_window() -> Win32Window:
    return get_window_by_title(get_game_process_name())


def move_window(window: Win32Window, window_settings: list):
    monitor_index = window_settings['monitor']
    if not monitor_index == None:
        move_window_to_monitor(window, monitor_index)
    width = window_settings['resolution']['x']
    height = window_settings['resolution']['y']
    if not width == None:
        set_window_size(window, width, height)
    

def window_checks(current_state: WindowAction):
    from settings import settings
    window_settings_list = settings['auto_move_windows']
    for window_settings in window_settings_list:
        settings_state = get_enum_from_val(ScriptStateType, window_settings['script_state'])
        if settings_state == current_state:
            title = window_settings['window_name']
            windows_to_change = get_windows_by_title(title)
            for window_to_change in windows_to_change:
                way_to_change_window = get_enum_from_val(WindowAction, window_settings['window_behaviour'])
                if way_to_change_window == WindowAction.MAX:
                    maximize_window(window_to_change)
                elif way_to_change_window == WindowAction.MIN:
                    minimize_window(window_to_change)
                elif way_to_change_window == WindowAction.CLOSE:
                    close_window(window_to_change)
                elif way_to_change_window == WindowAction.MOVE:
                    move_window(window_to_change, window_settings)
                # elif way_to_change_window == WindowAction.NONE:
                #     pass
                else:
                    print('invalid window behaviour specified in settings')