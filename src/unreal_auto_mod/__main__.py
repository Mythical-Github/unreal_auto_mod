import sys
from pathlib import Path

from unreal_auto_mod import cli_py
from unreal_auto_mod import log_py as log
from unreal_auto_mod.cli import OPTIONS
from unreal_auto_mod.log_info import LOG_INFO

if getattr(sys, 'frozen', False):
    SCRIPT_DIR = Path(sys.executable).parent
else:
    SCRIPT_DIR = Path(__file__).resolve().parent


def main():
    try:
        log.set_log_base_dir(SCRIPT_DIR)
        log.configure_logging(LOG_INFO)
        cli_py.cli_logic(OPTIONS)
    except Exception as error_message:
        log.log_message(str(error_message))


if __name__ == "__main__":
    main()
