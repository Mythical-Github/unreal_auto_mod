import os
import sys

from unreal_auto_mod import (
    customization,
    file_io,
    log_info,
    logger,
    main_logic,
    settings,
    window_management,
    wrapper,
)
from unreal_auto_mod.programs import repak, unreal_engine


def uproject_check():
    uproject_file = settings.get_uproject_file()
    if uproject_file:
        file_io.check_file_exists(uproject_file)
        logger.log_message("Check: Uproject file exists")


def unreal_engine_check():
    should_do_check = True

    if (
        not settings.is_unreal_pak_packing_enum_in_use()
        or settings.is_engine_packing_enum_in_use()
    ):
        should_do_check = False

    if should_do_check:
        engine_str = "UE4Editor"
        if unreal_engine.is_game_ue5(settings.get_unreal_engine_dir()):
            engine_str = "UnrealEditor"
        file_io.check_file_exists(
            f"{settings.get_unreal_engine_dir()}/Engine/Binaries/Win64/{engine_str}.exe"
        )
        logger.log_message("Check: Unreal Engine exists")


def game_launcher_exe_override_check():
    if settings.get_override_automatic_launcher_exe_finding():
        file_io.check_file_exists(settings.get_game_launcher_exe_path())


def git_info_check():
    git_repo_path = settings.get_git_info_repo_path()
    if git_repo_path is None or git_repo_path == "":
        return

    file_io.check_directory_exists(git_repo_path)


def game_exe_check():
    file_io.check_file_exists(settings.get_game_exe_path())


def initialization():
    window_management.change_window_name("unreal_auto_mod")
    if "--logs_directory" in sys.argv:
        index = sys.argv.index("--logs_directory") + 1
        if index < len(sys.argv):
            log_dir = f"{os.path.normpath(sys.argv[index].strip("'").strip('"'))}"
            logger.set_log_base_dir(log_dir)
            logger.configure_logging(log_info.LOG_INFO)
        else:
            logger.set_log_base_dir(os.path.normpath(f"{file_io.SCRIPT_DIR}/logs"))
            logger.configure_logging(log_info.LOG_INFO)
    else:
        logger.set_log_base_dir(os.path.normpath(f"{file_io.SCRIPT_DIR}/logs"))
        logger.configure_logging(log_info.LOG_INFO)
        customization.enable_vt100()
        main_logic.init_thread_system()
    check_generate_wrapper()
    check_settings()
    if settings.settings_information.init_settings_done:
        uproject_check()
        unreal_engine_check()
        game_launcher_exe_override_check()
        git_info_check()
        repak.ensure_repak_installed()
        # game_exe_check()

        if repak.get_is_using_repak_path_override():
            file_io.check_file_exists(repak.get_repak_path_override())
            logger.log_message("Check: Repak exists")

        logger.log_message("Check: Game exists")

        logger.log_message("Check: Passed all init checks")


def check_generate_wrapper():
    if "--generate_wrapper" in sys.argv:
        wrapper.generate_wrapper()


def check_settings():
    if "--settings_json" in sys.argv:
        index = sys.argv.index("--settings_json") + 1
        if index < len(sys.argv):
            settings_file = f"{os.path.normpath(sys.argv[index].strip("'").strip('"'))}"
            return settings.load_settings(settings_file)
        logger.log_message("Error: No file path provided after --settings_json.")
        sys.exit(1)
    return
