import logging
import os
from datetime import datetime
from shutil import get_terminal_size

from rich.logging import RichHandler

from unreal_auto_mod.console import console
from unreal_auto_mod.log_info import LOG_INFO

FORMAT = "%(message)s"

logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("rich")

log_base_dir = f'{os.getcwd()}/src'
log_prefix = ''


class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


def set_log_base_dir(base_dir: str):
    global log_base_dir
    log_base_dir = base_dir


def configure_logging(colors_config):
    global log_prefix

    log_prefix = colors_config['log_name_prefix']

    log_dir = os.path.join(log_base_dir, 'logs')
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    rename_latest_log(log_dir)

    file_handler = FlushFileHandler(os.path.join(log_dir, 'latest.log'))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(message)s'))

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


def log_message(message: str):
    color_options = LOG_INFO.get('theme_colors')
    default_background_color = LOG_INFO.get('background_color')
    default_background_color = f"rgb({default_background_color[0]},{default_background_color[1]},{default_background_color[2]})"

    default_text_color = LOG_INFO.get('default_color')
    default_text_color = f"rgb({default_text_color[0]},{default_text_color[1]},{default_text_color[2]})"
    terminal_width = get_terminal_size().columns
    padded_message = (message[:terminal_width] if len(message) > terminal_width else message.ljust(terminal_width))
    for keyword, color in color_options.items():
        if keyword in padded_message:
            rgb_color = f"rgb({color[0]},{color[1]},{color[2]})"
            console.print((padded_message), style=f'{rgb_color} on {default_background_color}')
            return
    console.print(padded_message, style=f'{default_text_color} on {default_background_color}')


def rename_latest_log(log_dir):
    latest_log_path = os.path.join(log_dir, 'latest.log')
    if os.path.isfile(latest_log_path):
        try:
            timestamp = datetime.now().strftime('%m_%d_%Y_%H%M_%S')
            new_name = f'{log_prefix}{timestamp}.log'
            new_log_path = os.path.join(log_dir, new_name)

            counter = 1
            while os.path.isfile(new_log_path) or is_file_in_use(latest_log_path):
                new_name = f'{log_prefix}{timestamp}_({counter}).log'
                new_log_path = os.path.join(log_dir, new_name)
                counter += 1

            os.rename(latest_log_path, new_log_path)

        except PermissionError as e:
            log_message(f"Error renaming log file: {e}")
            return


def is_file_in_use(file_path):
    try:
        with open(file_path, 'a'):
            return False
    except OSError:
        return True

