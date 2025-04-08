import os
import textwrap
from dataclasses import dataclass
from datetime import datetime
from shutil import get_terminal_size

from unreal_auto_mod.console import console
from unreal_auto_mod.log_info import LOG_INFO


@dataclass
class LogInformation:
    log_base_dir: str
    log_prefix: str


log_information = LogInformation(log_base_dir=f"{os.getcwd()}/src", log_prefix="")


def set_log_base_dir(base_dir: str):
    log_information.log_base_dir = base_dir


def configure_logging(colors_config):
    log_information.log_prefix = colors_config["log_name_prefix"]

    log_dir = os.path.join(log_information.log_base_dir)
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    rename_latest_log(log_dir)


def rename_latest_log(log_dir):
    latest_log_path = os.path.join(log_dir, f"{log_information.log_prefix}latest.log")
    if os.path.isfile(latest_log_path):
        try:
            timestamp = datetime.now().strftime("%m_%d_%Y_%H%M_%S")
            new_name = f"{log_information.log_prefix}{timestamp}.log"
            new_log_path = os.path.join(log_dir, new_name)

            # Ensure the new log file name is unique
            counter = 1
            while os.path.isfile(new_log_path):
                new_name = f"{log_information.log_prefix}{timestamp}_({counter}).log"
                new_log_path = os.path.join(log_dir, new_name)
                counter += 1

            os.rename(latest_log_path, new_log_path)

        except PermissionError as e:
            log_message(f"Error renaming log file: {e}")
            return


def log_message(message: str):
    color_options = LOG_INFO.get("theme_colors", {})
    default_background_color = LOG_INFO.get("background_color", (40, 42, 54))
    default_background_color = f"rgb({default_background_color[0]},{default_background_color[1]},{default_background_color[2]})"

    default_text_color = LOG_INFO.get("default_color", (94, 94, 255))
    default_text_color = (
        f"rgb({default_text_color[0]},{default_text_color[1]},{default_text_color[2]})"
    )

    terminal_width = get_terminal_size().columns
    wrapped_lines = textwrap.wrap(message, width=terminal_width)

    for line in enumerate(wrapped_lines):
        padded_line = line[1].ljust(terminal_width)
        for keyword, color in color_options.items():
            if keyword in message:
                rgb_color = f"rgb({color[0]},{color[1]},{color[2]})"
                console.print(
                    padded_line, style=f"{rgb_color} on {default_background_color}"
                )
                break
        else:
            console.print(
                padded_line, style=f"{default_text_color} on {default_background_color}"
            )

    log_dir = os.path.join(log_information.log_base_dir)
    log_path = os.path.join(log_dir, f"{log_information.log_prefix}latest.log")

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    if not os.path.isfile(log_path):
        try:
            with open(log_path, "w") as log_file:
                log_file.write("")
        except OSError as e:
            error_color = LOG_INFO.get("error_color", (255, 0, 0))
            error_color = f"rgb({error_color[0]},{error_color[1]},{error_color[2]})"
            console.print(
                f"Failed to create log file: {e}",
                style=f"{error_color} on {default_background_color}",
            )
            return

    try:
        with open(log_path, "a") as log_file:
            log_file.write(f"{message}\n")
    except OSError as e:
        error_color = LOG_INFO.get("error_color", (255, 0, 0))
        error_color = f"rgb({error_color[0]},{error_color[1]},{error_color[2]})"
        console.print(
            f"Failed to write to log file: {e}",
            style=f"{error_color} on {default_background_color}",
        )
