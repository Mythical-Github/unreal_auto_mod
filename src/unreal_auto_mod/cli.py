import json
import os
import pathlib

import click
import tomlkit
from trogon import tui

from unreal_auto_mod import (
    app_runner,
    data_structures,
    file_io,
    initialization,
    logger,
    main_logic,
    process_management,
    settings,
    unreal_collections,
    unreal_inis,
)
from unreal_auto_mod.programs import stove

default_logs_dir = os.path.normpath(f"{file_io.SCRIPT_DIR}/logs")
default_output_releases_dir = os.path.normpath(os.path.join(file_io.SCRIPT_DIR, "dist"))
default_releases_dir = os.path.normpath(
    os.path.join(
        settings.settings_information.settings_json_dir, "mod_packaging", "releases"
    )
)


@tui()
@click.version_option()
@click.group(chain=True)
@click.option(
    "--generate_wrapper",
    is_flag=True,
    default=False,
    type=bool,
    help="Generate a wrapper that contains the current commandline.",
)
# @click.option('--log_name_prefix', default='unreal_auto_mod_', type=str, help='The log name prefix for your logs.')
@click.option(
    "--logs_directory",
    default=default_logs_dir,
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
    help="The directory you want your logs outputted to.",
)
def cli(generate_wrapper, logs_directory, max_content_width=200):
    initialization.initialization()


command_help = "Builds the uproject specified within the settings JSON"


@cli.command(name="build", help=command_help, short_help=command_help)
@click.option(
    "--toggle_engine",
    is_flag=True,
    default=False,
    type=bool,
    help="Will close engine instances at the start and open at the end of the command process",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def build(settings_json, toggle_engine):
    main_logic.build(toggle_engine=toggle_engine)


command_help = "Cooks content for the uproject specified within the settings JSON"


@cli.command(name="cook", help=command_help, short_help=command_help)
@click.option(
    "--toggle_engine",
    is_flag=True,
    default=False,
    type=bool,
    help="Will close engine instances at the start and open at the end of the command process",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def cook(settings_json, toggle_engine):
    main_logic.cook(toggle_engine=toggle_engine)


command_help = "Package content for the uproject specified within the settings JSON"


@cli.command(name="package", help=command_help, short_help=command_help)
@click.option(
    "--toggle_engine",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to close engine instances at the start and open at the end of the command process",
)
@click.option(
    "--use_symlinks",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to use symlinks to save time with file operations",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def package(settings_json, toggle_engine, use_symlinks):
    main_logic.package(toggle_engine=toggle_engine, use_symlinks=use_symlinks)


command_help = "Run tests for specific mods"


@cli.command(name="test_mods", help=command_help, short_help=command_help)
@click.option(
    "--mod_names",
    multiple=True,
    type=str,
    required=True,
    help="A mod name, can be specified multiple times",
)
@click.option(
    "--toggle_engine",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to close engine instances at the start and open at the end of the command process",
)
@click.option(
    "--use_symlinks",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to use symlinks to save time with file operations",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def test_mods(settings_json, mod_names, toggle_engine, use_symlinks):
    main_logic.test_mods(
        input_mod_names=mod_names,
        toggle_engine=toggle_engine,
        use_symlinks=use_symlinks,
    )


command_help = "Run tests for all mods within the specified settings JSON"


@cli.command(name="test_mods_all", help=command_help, short_help=command_help)
@click.option(
    "--toggle_engine",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to close engine instances at the start and open at the end of the command process",
)
@click.option(
    "--use_symlinks",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to use symlinks to save time with file operations",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def test_mods_all(settings_json, toggle_engine, use_symlinks):
    main_logic.test_mods_all(toggle_engine=toggle_engine, use_symlinks=use_symlinks)


command_help = "Builds, Cooks, Packages, Generates Mods, and Generates Mod Releases for the specified mod names."


@cli.command(name="full_run", help=command_help, short_help=command_help)
@click.option(
    "--mod_names",
    multiple=True,
    type=str,
    required=True,
    help="A mod name, can be specified multiple times",
)
@click.option(
    "--toggle_engine",
    is_flag=True,
    default=False,
    type=bool,
    help="Will close engine instances at the start and open at the end of the command process",
)
@click.option(
    "--base_files_directory",
    default=default_releases_dir,
    help="Path to dir tree whose content to pack alongside the mod for release",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
@click.option(
    "--output_directory",
    default=default_output_releases_dir,
    help="Path to the output directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
@click.option(
    "--use_symlinks",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to use symlinks to save time with file operations",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def full_run(
    settings_json,
    mod_names,
    toggle_engine,
    base_files_directory,
    output_directory,
    use_symlinks,
):
    main_logic.full_run(
        input_mod_names=mod_names,
        toggle_engine=toggle_engine,
        base_files_directory=base_files_directory,
        output_directory=output_directory,
        use_symlinks=use_symlinks,
    )


command_help = "Builds, Cooks, Packages, Generates Mods, and Generates Mod Releases for all mod entries within the specified settings JSON."


@cli.command(name="full_run_all", help=command_help, short_help=command_help)
@click.option(
    "--toggle_engine",
    is_flag=True,
    default=False,
    type=bool,
    help="Will close engine instances at the start and open at the end of the command process",
)
@click.option(
    "--base_files_directory",
    default=default_releases_dir,
    help="Path to dir tree whose content to pack alongside the mod for release",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
@click.option(
    "--output_directory",
    default=default_output_releases_dir,
    help="Path to the output directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
@click.option(
    "--use_symlinks",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to use symlinks to save time with file operations",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def full_run_all(
    settings_json, toggle_engine, base_files_directory, output_directory, use_symlinks
):
    main_logic.full_run_all(
        toggle_engine=toggle_engine,
        base_files_directory=base_files_directory,
        output_directory=output_directory,
        use_symlinks=use_symlinks,
    )


command_help = "Generates mods for the specified mod names."


@cli.command(name="generate_mods", help=command_help, short_help=command_help)
@click.option(
    "--mod_names",
    multiple=True,
    type=str,
    required=True,
    help="A mod name, can be specified multiple times",
)
@click.option(
    "--use_symlinks",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to use symlinks to save time with file operations",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def generate_mods(settings_json, mod_names, use_symlinks):
    main_logic.generate_mods(input_mod_names=mod_names, use_symlinks=use_symlinks)


command_help = "Generates mods for all enabled mods within the specified settings JSON."


@cli.command(name="generate_mods_all", help=command_help, short_help=command_help)
@click.option(
    "--use_symlinks",
    is_flag=True,
    default=False,
    type=bool,
    help="Whether or not to use symlinks to save time with file operations",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def generate_mods_all(settings_json, use_symlinks):
    main_logic.generate_mods_all(use_symlinks=use_symlinks)


command_help = "Generate one or more mod releases."


@cli.command(name="generate_mod_releases", help=command_help, short_help=command_help)
@click.option(
    "--mod_names",
    multiple=True,
    type=str,
    required=True,
    help="A mod name, can be specified multiple times",
)
@click.option(
    "--base_files_directory",
    default=default_releases_dir,
    help="Path to dir tree whose content to pack alongside the mod for release",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "--output_directory",
    default=default_output_releases_dir,
    help="Path to the output directory",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def generate_mod_releases(
    settings_json, mod_names, base_files_directory, output_directory
):
    main_logic.generate_mod_releases(mod_names, base_files_directory, output_directory)


command_help = "Generate mod releases for all mods within the specified settings JSON."


@cli.command(
    name="generate_mod_releases_all", help=command_help, short_help=command_help
)
@click.option(
    "--base_files_directory",
    default=default_releases_dir,
    help="Path to dir tree whose content to pack alongside the mod for release",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "--output_directory",
    default=default_output_releases_dir,
    help="Path to the output directory",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def generate_mod_releases_all(settings_json, base_files_directory, output_directory):
    main_logic.generate_mod_releases_all(base_files_directory, output_directory)


command_help = "Cleans up the GitHub repository specified within the settings JSON."


@cli.command(name="cleanup_full", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def cleanup_full(settings_json):
    main_logic.cleanup_full()


command_help = "Cleans up the directories made from cooking of the GitHub repository specified within the settings JSON."


@cli.command(name="cleanup_cooked", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def cleanup_cooked(settings_json):
    main_logic.cleanup_cooked()


command_help = "Cleans up the directories made from building of the GitHub repository specified within the settings JSON."


@cli.command(name="cleanup_build", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def cleanup_build(settings_json):
    main_logic.cleanup_build()


command_help = """
Cleans up the specified directory, deleting all files not specified within the file list JSON.
To generate a file list JSON, use the generate_file_list_json command.
"""


@cli.command(name="cleanup_game", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def cleanup_game(settings_json):
    main_logic.cleanup_game()


command_help = "Generates a JSON file containing all of the files in the game directory, from the game exe specified within the settings JSON."


@cli.command(
    name="generate_game_file_list_json", help=command_help, short_help=command_help
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def generate_game_file_list_json(settings_json):
    main_logic.generate_game_file_list_json()


command_help = """
Cleans up the specified directory, deleting all files not specified within the file list JSON.
To generate one, use the generate_file_list command.
"""


@cli.command(name="cleanup_from_file_list", help=command_help, short_help=command_help)
@click.argument(
    "file_list",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.argument(
    "directory",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
def cleanup_from_file_list(file_list, directory):
    """
    Arguments:
        file_list (str): Path to the file list you want to clean from.
        directory (str): Path to the directory tree to clean up. It will delete all files not in the specified file list.
    """
    main_logic.cleanup_from_file_list(file_list, directory)


command_help = (
    "Generates a JSON file containing all of the files in the specified directory."
)


@cli.command(name="generate_file_list", help=command_help, short_help=command_help)
@click.argument(
    "directory",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.argument(
    "file_list",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
def generate_file_list(directory, file_list):
    """
    Arguments:
        directory (str): Path to the directory tree you want to generate the file list from.
        file_list (str): Path to the output file, saved in JSON format.
    """
    main_logic.generate_file_list(directory, file_list)


command_help = "Uploads the latest changes of the git project to the GitHub repository and branch specified within the settings JSON."


@cli.command(name="upload_changes_to_repo", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def upload_changes_to_repo(settings_json):
    main_logic.upload_changes_to_repo()


command_help = "Cleans up and resyncs a git project to the GitHub repository and branch specified within the settings JSON."


@cli.command(name="resync_dir_with_repo", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def resync_dir_with_repo(settings_json):
    main_logic.resync_dir_with_repo()


command_help = "Opens the latest log file."


@cli.command(name="open_latest_log", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def open_latest_log(settings_json):
    main_logic.open_latest_log()


command_help = "Enable the given mod names in the provided settings JSON."


@cli.command(name="enable_mods", help=command_help, short_help=command_help)
@click.option(
    "--mod_names",
    multiple=True,
    type=str,
    required=True,
    help="Name of a mod to enable, can be specified multiple times",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def enable_mods(settings_json, mod_names):
    main_logic.enable_mods(settings_json=settings_json, mod_names=mod_names)


command_help = "Disable the given mod names in the provided settings JSON."


@cli.command(name="disable_mods", help=command_help, short_help=command_help)
@click.option(
    "--mod_names",
    multiple=True,
    type=str,
    required=True,
    help="Name of a mod to disable, can be specified multiple times",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def disable_mods(settings_json, mod_names):
    main_logic.disable_mods(settings_json=settings_json, mod_names=mod_names)


command_help = "Adds the given mod name in the provided settings JSON."


@cli.command(name="add_mod", help=command_help, short_help=command_help)
@click.option(
    "--packing_type",
    type=click.Choice(["unreal_pak", "repak", "engine", "loose"]),
    help="Packing type for the mod.",
    required=True,
    default="unreal_pak",
)
@click.option(
    "--mod_name_dir_type",
    type=str,
    default="Mods",
    help='Directory type for the mod name (default: "Mods").',
)
@click.option(
    "--use_mod_name_dir_name_override",
    type=bool,
    default=False,
    help="Whether to override the mod name directory (default: False).",
)
@click.option(
    "--mod_name_dir_name_override",
    type=str,
    default=None,
    help="Override the mod name directory with this value (optional).",
)
@click.option(
    "--pak_chunk_num", type=int, default=None, help="Pak chunk number (optional)."
)
@click.option(
    "--compression_type",
    default="",
    type=str,
    help="Compression type for the mod (optional).",
)
@click.option(
    "--is_enabled",
    type=bool,
    default=True,
    help="Whether the mod is enabled (default: True).",
)
@click.option(
    "--asset_paths",
    multiple=True,
    help="Asset path for the mod, can be specified multiple times.",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "--tree_paths",
    multiple=True,
    help="Tree path for the mod, can be specified multiple times.",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
@click.argument("mod_name", type=str)
@click.argument("pak_dir_structure", type=str)
def add_mod(
    settings_json,
    mod_name,
    packing_type,
    pak_dir_structure,
    mod_name_dir_type,
    use_mod_name_dir_name_override,
    mod_name_dir_name_override,
    pak_chunk_num,
    compression_type,
    is_enabled,
    asset_paths,
    tree_paths,
):
    """
    Arguments:
        mod_name (str): The name of the mod to add.
        pak_dir_structure (str): Path to the directory structure for packing.
    """
    main_logic.add_mod(
        settings_json=settings_json,
        mod_name=mod_name,
        packing_type=packing_type,
        pak_dir_structure=pak_dir_structure,
        mod_name_dir_type=mod_name_dir_type,
        use_mod_name_dir_name_override=use_mod_name_dir_name_override,
        mod_name_dir_name_override=mod_name_dir_name_override,
        pak_chunk_num=pak_chunk_num,
        compression_type=compression_type,
        is_enabled=is_enabled,
        asset_paths=asset_paths,
        tree_paths=tree_paths,
    )


command_help = "Removes the given mod names in the provided settings JSON."


@cli.command(name="remove_mods", help=command_help, short_help=command_help)
@click.option(
    "--mod_names",
    multiple=True,
    type=str,
    required=True,
    help="Name of a mod to be removed, can be specified multiple times.",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def remove_mods(settings_json, mod_names):
    main_logic.remove_mods(settings_json=settings_json, mod_names=mod_names)


command_help = "Run the game."


@cli.command(name="run_game", help=command_help, short_help=command_help)
@click.option(
    "--toggle_engine",
    default=False,
    type=bool,
    help="Whether to close engine instances at the start and open at the end of the command process (default: False).",
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def run_game(settings_json, toggle_engine):
    main_logic.run_game(toggle_engine=toggle_engine)


command_help = "Close the game."


@cli.command(name="close_game", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def close_game(settings_json):
    main_logic.close_game()


command_help = "Run the engine."


@cli.command(name="run_engine", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def run_engine(settings_json):
    main_logic.run_engine()


command_help = "Close the engine."


@cli.command(name="close_engine", help=command_help, short_help=command_help)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def close_engine(settings_json):
    main_logic.close_engine()


command_help = (
    "Generates a uproject file at the specified location, using the given information."
)


@cli.command(name="generate_uproject", help=command_help, short_help=command_help)
@click.option(
    "--file_version",
    default=3,
    type=int,
    help="Uproject file specification. Defaults to 3.",
)
@click.option(
    "--engine_major_association",
    default=4,
    type=int,
    help="Major Unreal Engine version for the project. Example: the 4 in 4.27.",
)
@click.option(
    "--engine_minor_association",
    default=27,
    type=int,
    help="Minor Unreal Engine version for the project. Example: the 27 in 4.27.",
)
@click.option(
    "--category", default="Modding", type=str, help="Category for the uproject."
)
@click.option(
    "--description",
    default="Uproject for modding, generated with unreal_auto_mod.",
    type=str,
    help="Description for the uproject.",
)
@click.option(
    "--ignore_safety_checks",
    default=False,
    type=bool,
    help="Whether or not to override the input checks for this command.",
)
@click.argument(
    "project_file",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
def generate_uproject(
    project_file,
    file_version,
    engine_major_association,
    engine_minor_association,
    category,
    description,
    ignore_safety_checks,
):
    """
    Arguments:
        project_file (str): Path to generate the project file at.
    """
    main_logic.generate_uproject(
        project_file=project_file,
        file_version=file_version,
        engine_major_association=engine_major_association,
        engine_minor_association=engine_minor_association,
        category=category,
        description=description,
        ignore_safety_checks=ignore_safety_checks,
    )


host_type_choices = data_structures.get_enum_strings_from_enum(
    data_structures.UnrealHostTypes
)
loading_phase_choices = data_structures.get_enum_strings_from_enum(
    data_structures.LoadingPhases
)

command_help = "Adds the specified module entry to the descriptor file, overwriting if it already exists."


@cli.command(
    name="add_module_to_descriptor", help=command_help, short_help=command_help
)
@click.option(
    "--host_type",
    type=click.Choice(host_type_choices),
    default=data_structures.UnrealHostTypes.DEVELOPER.value,
    required=True,
    help="The host type to use.",
)
@click.option(
    "--loading_phase",
    type=click.Choice(loading_phase_choices),
    default=data_structures.LoadingPhases.DEFAULT.value,
    required=True,
    help="The loading phase to use.",
)
@click.argument(
    "descriptor_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.argument("module_name", type=str)
def add_module_to_descriptor(descriptor_file, module_name, host_type, loading_phase):
    """
    Arguments:
        descriptor_file (str): Path to the descriptor file to add the module to.
        module_name (str): Name of the module to add.
    """
    main_logic.add_module_to_descriptor(
        descriptor_file, module_name, host_type, loading_phase
    )


command_help = "Adds the specified plugin entry to the descriptor file, overwriting if it already exists."


@cli.command(
    name="add_plugin_to_descriptor", help=command_help, short_help=command_help
)
@click.option(
    "--is_enabled",
    default=True,
    type=bool,
    help="Whether or not Enabled is ticked for the plugin entry.",
)
@click.argument(
    "descriptor_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
@click.argument("plugin_name", type=str)
def add_plugin_to_descriptor(descriptor_file, plugin_name, is_enabled):
    """
    Arguments:
        descriptor_file (str): Path to the descriptor file to add the plugin to.
        plugin_name (str): Name of the plugin to add.
    """
    main_logic.add_plugin_to_descriptor(
        descriptor_file, plugin_name, is_enabled=is_enabled
    )


command_help = (
    "Removes the module name entries in the provided descriptor file if they exist."
)


@cli.command(
    name="remove_modules_from_descriptor", help=command_help, short_help=command_help
)
@click.option(
    "--module_names",
    multiple=True,
    type=str,
    required=True,
    help="A module name to remove from the descriptor file, can be specified multiple times.",
)
@click.argument(
    "descriptor_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
def remove_modules_from_descriptor(descriptor_file, module_names):
    """
    Arguments:
        descriptor_file (str): Path to the descriptor file to remove the modules from.
    """
    main_logic.remove_modules_from_descriptor(descriptor_file, module_names)


command_help = (
    "Removes the plugin name entries in the provided descriptor file if they exist."
)


@cli.command(
    name="remove_plugins_from_descriptor", help=command_help, short_help=command_help
)
@click.option(
    "--plugin_names",
    multiple=True,
    type=str,
    required=True,
    help="A plugin name to remove from the descriptor file, can be specified multiple times.",
)
@click.argument(
    "descriptor_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
)
def remove_plugins_from_descriptor(descriptor_file, plugin_names):
    """
    Arguments:
        descriptor_file (str): Path to the descriptor file to remove the plugins from.
    """
    main_logic.remove_plugins_from_descriptor(descriptor_file, plugin_names)


command_help = "Generates a uplugin in a directory, within the specified directory with the given settings."


@cli.command(name="generate_uplugin", help=command_help, short_help=command_help)
@click.option(
    "--can_contain_content",
    default=True,
    type=bool,
    help="Whether the plugin can contain content.",
)
@click.option(
    "--is_installed", default=True, type=bool, help="Whether the plugin is installed."
)
@click.option(
    "--is_hidden", default=False, type=bool, help="Whether the plugin is hidden."
)
@click.option(
    "--no_code",
    default=False,
    type=bool,
    help="Whether the plugin should contain code.",
)
@click.option(
    "--category", default="Modding", type=str, help="Category for the plugin."
)
@click.option(
    "--created_by", default="", type=str, help="Name of the creator of the plugin."
)
@click.option(
    "--created_by_url", default="", type=str, help="URL of the creator of the plugin."
)
@click.option("--description", default="", type=str, help="Description of the plugin.")
@click.option(
    "--docs_url", default="", type=str, help="Documentation URL for the plugin."
)
@click.option(
    "--editor_custom_virtual_path",
    default="",
    type=str,
    help="Custom virtual path for the editor.",
)
@click.option(
    "--enabled_by_default",
    default=True,
    type=str,
    help="Whether the plugin is enabled by default.",
)
@click.option(
    "--engine_major_version",
    default=4,
    type=int,
    help="Major Unreal Engine version for the plugin.",
)
@click.option(
    "--engine_minor_version",
    default=27,
    type=int,
    help="Minor Unreal Engine version for the plugin.",
)
@click.option("--support_url", default="", type=str, help="Support URL for the plugin.")
@click.option("--version", default=1.0, type=float, help="Version of the plugin.")
@click.option(
    "--version_name", default="", type=str, help="Version name of the plugin."
)
@click.argument(
    "plugins_directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
@click.argument("plugin_name", type=str)
def generate_uplugin(
    plugins_directory,
    plugin_name,
    can_contain_content,
    is_installed,
    is_hidden,
    no_code,
    category,
    created_by,
    created_by_url,
    description,
    docs_url,
    editor_custom_virtual_path,
    enabled_by_default,
    engine_major_version,
    engine_minor_version,
    support_url,
    version,
    version_name,
):
    """
    Arguments:
        plugins_directory (str): Path to the plugins directory, mainly for use with Uproject plugins folder, and engine plugins folder.
        plugin_name (str): Name of the plugin to be generated.
    """
    # enabled_by_default: bool,
    # can_contain_content: bool,
    # is_installed: bool,
    # is_hidden: bool,
    # no_code: bool,
    main_logic.generate_uplugin(
        plugins_directory=plugins_directory,
        plugin_name=plugin_name,
        category=category,
        created_by=created_by,
        created_by_url=created_by_url,
        description=description,
        docs_url=docs_url,
        editor_custom_virtual_path=editor_custom_virtual_path,
        engine_major_version=engine_major_version,
        engine_minor_version=engine_minor_version,
        support_url=support_url,
        version=version,
        version_name=version_name,
        enabled_by_default=enabled_by_default,
        can_contain_content=can_contain_content,
        is_installed=is_installed,
        is_hidden=is_hidden,
        no_code=no_code,
    )


command_help = "Deletes all files for the specified uplugin paths."


@cli.command(name="remove_uplugins", help=command_help, short_help=command_help)
@click.option(
    "--uplugin_paths",
    multiple=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="uplugin_paths: A path to a uplugin to delete, can be specified multiple times.",
)
def remove_uplugins(uplugin_paths):
    main_logic.remove_uplugins(uplugin_paths)


command_help = "Resaves packages and fixes up redirectors for the project."


@cli.command(
    name="resave_packages_and_fix_up_redirectors",
    help=command_help,
    short_help=command_help,
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
    help="Path to the settings JSON file",
)
def resave_packages_and_fix_up_redirectors(settings_json):
    main_logic.resave_packages_and_fix_up_redirectors()


command_help = "Closes all programs with the exe names provided."


@cli.command(name="close_programs", help=command_help, short_help=command_help)
@click.option(
    "--exe_names",
    multiple=True,
    type=str,
    required=True,
    help="Name of an executable to be closed, can be specified multiple times.",
)
def close_programs(exe_names):
    process_management.close_programs(exe_names)


command_help = "Install Fmodel."


@cli.command(name="install_fmodel", help=command_help, short_help=command_help)
@click.option(
    "--run_after_install",
    is_flag=True,
    default=False,
    type=bool,
    help="Should the installed program be run after installation.",
)
@click.argument(
    "output_directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
def install_fmodel(output_directory, run_after_install):
    """
    Arguments:
        output_directory (str): Path to the output directory
    """
    main_logic.install_fmodel(output_directory=output_directory, run_after_install=run_after_install)


command_help = "Install Umodel."


@cli.command(name="install_umodel", help=command_help, short_help=command_help)
@click.option(
    "--run_after_install",
    is_flag=True,
    default=False,
    type=bool,
    help="Should the installed program be run after installation.",
)
@click.argument(
    "output_directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
def install_umodel(output_directory, run_after_install):
    """
    Arguments:
        output_directory (str): Path to the output directory
    """
    main_logic.install_umodel(output_directory=output_directory, run_after_install=run_after_install)


command_help = "Install Stove."


@cli.command(name="install_stove", help=command_help, short_help=command_help)
@click.argument(
    "output_directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
@click.option(
    "--run_after_install",
    is_flag=True,
    default=False,
    type=bool,
    help="Should the installed program be run after installation.",
)
def install_stove(output_directory, run_after_install):
    """
    Arguments:
        output_directory (str): Path to the output directory
    """
    if not stove.does_stove_exist(output_directory):
        stove.install_stove(output_directory)
    if run_after_install:
        app_runner.run_app(stove.get_stove_path(output_directory))


command_help = "Install Spaghetti."


@cli.command(name="install_spaghetti", help=command_help, short_help=command_help)
@click.option(
    "--run_after_install",
    is_flag=True,
    default=False,
    type=bool,
    help="Should the installed program be run after installation.",
)
@click.argument(
    "output_directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
def install_spaghetti(output_directory, run_after_install):
    """
    Arguments:
        output_directory (str): Path to the output directory
    """
    main_logic.install_spaghetti(output_directory=output_directory, run_after_install=run_after_install)


command_help = "Install UAssetGUI."


@cli.command(name="install_uasset_gui", help=command_help, short_help=command_help)
@click.option(
    "--run_after_install",
    is_flag=True,
    default=False,
    type=bool,
    help="Should the installed program be run after installation.",
)
@click.argument(
    "output_directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
def install_uasset_gui(output_directory, run_after_install):
    """
    Arguments:
        output_directory (str): Path to the output directory
    """
    main_logic.install_uasset_gui(output_directory=output_directory, run_after_install=run_after_install)


command_help = "Install Kismet Analyzer."


@cli.command(name="install_kismet_analyzer", help=command_help, short_help=command_help)
@click.option(
    "--run_after_install",
    is_flag=True,
    default=False,
    type=bool,
    help="Should the installed program be run after installation.",
)
@click.argument(
    "output_directory",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
)
def install_kismet_analyzer(output_directory, run_after_install):
    """
    Arguments:
        output_directory (str): Path to the output directory
    """
    main_logic.install_kismet_analyzer(
        output_directory=output_directory, run_after_install=run_after_install
    )


file_content_options = data_structures.get_enum_strings_from_enum(
    unreal_collections.UnrealContentLineType
)
command_help = "Create Collection"
default_create_collection_guid = unreal_collections.UnrealGuid.generate_unreal_guid()
default_parent_guid = unreal_collections.get_blank_unreal_guid().to_uid()


@cli.command(name="create_collection", help=command_help, short_help=command_help)
@click.option(
    "--collection_path",
    type=click.Path(exists=False, resolve_path=True, path_type=pathlib.Path),
    help="The path to the collection file to edit.",
    required=True,
)
@click.option(
    "--file_version", type=int, default=2, help="The collection file version."
)
@click.option(
    "--content_type",
    default=file_content_options[0],
    type=click.Choice(file_content_options),
    help="The type of content collection, dynamic uses file filters, static uses manual specification",
)
@click.option(
    "--guid",
    default=default_create_collection_guid,
    type=str,
    help="The guid of the collection, if not provided one will be automatically generated.",
)
@click.option(
    "--parent_guid",
    default=default_parent_guid,
    type=str,
    help="The parent guid of the collection, if not provided no parent is assumed, and a blank one is given.",
)
@click.option(
    "--red", default=0.0, type=float, help="The value of the color, accepts 0.0-1.0."
)
@click.option(
    "--green", default=0.0, type=float, help="The value of the color, accepts 0.0-1.0."
)
@click.option(
    "--blue", default=0.0, type=float, help="The value of the color, accepts 0.0-1.0."
)
@click.option(
    "--alpha", default=0.0, type=float, help="The value of the color, accepts 0.0-1.0."
)
@click.option(
    "--file_paths",
    type=str,
    multiple=True,
    help="A list of file paths to include in the collection, they will be automatically converted into unreal asset paths. For use with static collections.",
)
@click.option(
    "--unreal_asset_paths",
    type=str,
    multiple=True,
    help="A list of unreal asset paths for the collection, for static collections.",
)
@click.option(
    "--filter_lines",
    type=str,
    multiple=True,
    help="A list of asset filter for the collection, for use with dynamic collections.",
)
def create_collection(
    collection_path: pathlib.Path,
    file_version: int,
    content_type: str,
    guid: str,
    parent_guid: str,
    red: float,
    green: float,
    blue: float,
    alpha: float,
    file_paths: list[str],
    unreal_asset_paths: list[str],
    filter_lines: list[str],
):
    type_of_content = data_structures.get_enum_from_val(
        unreal_collections.UnrealContentLineType, content_type
    )
    content_lines = []
    os.makedirs(os.path.dirname(collection_path), exist_ok=True)
    if type_of_content == unreal_collections.UnrealContentLineType.STATIC:
        for file_path in file_paths:
            content_lines.append(unreal_collections.UnrealAssetPath(path=file_path))
        for unreal_asset_path in unreal_asset_paths:
            content_lines.append(
                unreal_collections.UnrealAssetPath(
                    unreal_collections.UnrealAssetPath.static_from_asset_reference(
                        unreal_asset_path
                    )
                )
            )
    if type_of_content == unreal_collections.UnrealContentLineType.DYNAMIC:
        content_lines = filter_lines
    unreal_collections.create_collection(
        collection_name=os.path.basename(collection_path),
        collections_directory=pathlib.Path(os.path.dirname(collection_path)),
        file_version=file_version,
        collection_type=unreal_collections.UnrealContentLineType(type_of_content),
        guid=unreal_collections.UnrealGuid.from_uid(guid),
        parent_guid=unreal_collections.UnrealGuid.from_uid(parent_guid),
        color=unreal_collections.UnrealCollectionColor(r=red, g=green, b=blue, a=alpha),
        content_lines=content_lines,
        exist_ok=True,
    )


command_help = "Set Collection Color"


@cli.command(
    name="set_color_from_collection_path", help=command_help, short_help=command_help
)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to edit.",
    required=True,
)
@click.option(
    "--red", default=0.0, type=float, help="The value of the color, accepts 0.0-1.0."
)
@click.option(
    "--green", default=0.0, type=float, help="The value of the color, accepts 0.0-1.0."
)
@click.option(
    "--blue", default=0.0, type=float, help="The value of the color, accepts 0.0-1.0."
)
@click.option(
    "--alpha", default=0.0, type=float, help="The value of the color, accepts 0.0-1.0."
)
def set_color_from_collection_path(
    collection_path: pathlib.Path, red: float, green: float, blue: float, alpha: float
):
    unreal_collections.set_color_from_collection_path(
        collection_path,
        unreal_collections.UnrealCollectionColor(r=red, g=green, b=blue, a=alpha),
    )


command_help = "Rename Collection"


@cli.command(name="rename_collection", help=command_help, short_help=command_help)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to rename.",
    required=True,
)
@click.option(
    "--new_name", type=str, help="New name for the collection.", required=True
)
def rename_collection(collection_path: str, new_name: str):
    unreal_collections.rename_collection_from_collection_path(pathlib.Path(collection_path), new_name)


command_help = "Delete Collection"


@cli.command(name="delete_collection", help=command_help, short_help=command_help)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to rename.",
    required=True,
)
def delete_collection(collection_path: str):
    unreal_collections.delete_collection(collection_path)


command_help = "Disable Collection"


@cli.command(name="disable_collection", help=command_help, short_help=command_help)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to rename.",
    required=True,
)
def disable_collection(collection_path: str):
    unreal_collections.disable_collection(collection_path)


command_help = "Enable Collection"


@cli.command(name="enable_collection", help=command_help, short_help=command_help)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to rename.",
    required=True,
)
def enable_collection(collection_path: str):
    unreal_collections.enable_collection(unreal_collections.get_unreal_collection_from_unreal_collection_path(pathlib.Path(collection_path)))


command_help = "Set Guid"
default_set_guid_from_collection_path_guid = unreal_collections.UnrealGuid.to_uid(
    unreal_collections.UnrealGuid(unreal_collections.UnrealGuid.generate_unreal_guid())
)


@cli.command(
    name="set_guid_from_collection_path", help=command_help, short_help=command_help
)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to rename.",
    required=True,
)
@click.option(
    "--guid",
    default=default_set_guid_from_collection_path_guid,
    type=str,
    help="The new guid in string form for the collection.",
)
def set_guid_from_collection_path(collection_path: str, guid: str):
    unreal_collections.set_guid_from_collection_path(
        collection_path=pathlib.Path(collection_path),
        guid=unreal_collections.UnrealGuid.from_uid(guid),
    )


command_help = "Set Parent Guid"


@cli.command(
    name="set_parent_guid_from_collection_path",
    help=command_help,
    short_help=command_help,
)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to rename.",
    required=True,
)
@click.option(
    "--parent_guid",
    default=default_parent_guid,
    type=str,
    help="The new parent guid in string form for the collection.",
)
def set_parent_guid_from_collection_path(collection_path: str, parent_guid: str):
    unreal_collections.set_parent_guid_from_collection_path(
        collection_path=pathlib.Path(collection_path),
        parent_guid=unreal_collections.UnrealGuid(parent_guid),
    )


command_help = "Set File Version"


@cli.command(
    name="set_file_version_from_collection_path",
    help=command_help,
    short_help=command_help,
)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to change the file version of.",
    required=True,
)
@click.option(
    "--file_version",
    default=2,
    type=int,
    help="The new file version for the collection.",
)
def set_file_version_from_collection_path(collection_path: str, file_version: int):
    unreal_collections.set_file_version_from_collection_path(collection_path=pathlib.Path(collection_path), file_version=file_version)


set_content_type_options = data_structures.get_enum_strings_from_enum(
    unreal_collections.UnrealContentLineType
)
command_help = "Set Collection Type"


@cli.command(
    name="set_collection_type_from_collection_path",
    help=command_help,
    short_help=command_help,
)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to change the file version of.",
    required=True,
)
@click.option(
    "--collection_type",
    default=unreal_collections.UnrealContentLineType.STATIC.value,
    type=click.Choice(set_content_type_options),
    help="The new content type for the collection, Static or Dynamic.",
)
def set_collection_type_from_collection_path(
    collection_path: str, collection_type: str
):
    type_to_pass = data_structures.get_enum_from_val(
        unreal_collections.UnrealContentLineType, collection_type
    )
    unreal_collections.set_collection_type_from_collection_path(
        collection_path=pathlib.Path(collection_path), collection_type=unreal_collections.UnrealContentLineType(type_to_pass)
    )


command_help = "Add content lines to collection file, Dynamic accepts filter lines, while Static accepts content path lines and unreal asset path lines"


@cli.command(
    name="add_content_lines_to_collection", help=command_help, short_help=command_help
)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to edit.",
    required=True,
)
@click.option(
    "--content_path_lines",
    type=str,
    help="The new content lines to add to the collection, they will be converted to unreal asset paths.",
    multiple=True,
    default=[],
)
@click.option(
    "--filter_lines",
    type=str,
    help="The new content filter lines to add to the collection.",
    multiple=True,
    default=[],
)
@click.option(
    "--unreal_asset_paths",
    type=str,
    help="The new unreal asset path lines to add to the collection.",
    multiple=True,
    default=[],
)
def add_content_lines_to_collection(
    collection_path: str,
    content_path_lines: list[str],
    filter_lines: list[str],
    unreal_asset_paths: list[str],
):
    collection = unreal_collections.get_unreal_collection_from_unreal_collection_path(
        pathlib.Path(collection_path)
    )
    collection_type = collection.content_type
    content_lines = []
    if collection_type == unreal_collections.UnrealContentLineType.DYNAMIC:
        content_lines.extend(filter_lines)

    if collection_type == unreal_collections.UnrealContentLineType.STATIC:
        for content_path_line in content_path_lines:
            content_lines.append(unreal_collections.UnrealAssetPath(content_path_line))

        for unreal_asset_path in unreal_asset_paths:
            test_one = unreal_collections.UnrealAssetPath.static_from_asset_reference(
                unreal_asset_path
            )
            test_two = unreal_collections.UnrealAssetPath(test_one)
            content_lines.append(test_two)
    unreal_collections.add_content_lines_to_collection(
        collection=collection, content_lines=content_lines
    )


command_help = "Remove content lines from collection file, Dynamic accepts filter lines, while Static accepts content path lines and unreal asset path lines"


@cli.command(
    name="remove_content_lines_from_collection",
    help=command_help,
    short_help=command_help,
)
@click.option(
    "--collection_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to edit.",
    required=True,
)
@click.option(
    "--content_path_lines",
    type=str,
    help="The new content lines to remove from the collection, they will be converted to unreal asset paths.",
    multiple=True,
    default=[],
)
@click.option(
    "--filter_lines",
    type=str,
    help="The new content filter lines to remove from the collection.",
    multiple=True,
    default=[],
)
@click.option(
    "--unreal_asset_paths",
    type=str,
    help="The new unreal asset path lines to remove from the collection.",
    multiple=True,
    default=[],
)
def remove_content_lines_from_collection(
    collection_path: str,
    content_path_lines: list[str],
    filter_lines: list[str],
    unreal_asset_paths: list[str],
):
    collection = unreal_collections.get_unreal_collection_from_unreal_collection_path(
        pathlib.Path(collection_path)
    )
    content_lines = []

    if collection.content_type == unreal_collections.UnrealContentLineType.DYNAMIC:
        content_lines.extend(filter_lines)

    if collection.content_type == unreal_collections.UnrealContentLineType.STATIC:
        for content_path_line in content_path_lines:
            content_lines.append(unreal_collections.UnrealAssetPath(content_path_line))

        for unreal_asset_path in unreal_asset_paths:
            content_lines.append(
                unreal_collections.UnrealAssetPath(
                    unreal_collections.UnrealAssetPath.static_from_asset_reference(
                        unreal_asset_path
                    )
                )
            )

    unreal_collections.remove_content_lines_from_collection(
        collection=collection, content_lines=content_lines
    )


command_help = "Add collections to the mod entry in the settings json"


@cli.command(
    name="add_collections_to_mod_entry", help=command_help, short_help=command_help
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the settings json, who's mod entry you want to add collections to.",
    required=True,
)
@click.option(
    "--mod_name",
    type=str,
    help="The mod name of the mod entry in the settings json to add the collection(s) to.",
    required=True,
)
@click.option(
    "--collection_paths",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to a collection to add to the settings json, can be specified multiple times.",
    default=[],
    multiple=True,
)
def add_collections_to_mod_entry(
    settings_json: pathlib.Path, mod_name: str, collection_paths: list[pathlib.Path]
):
    collections_to_pass = []
    for collection_path in collection_paths:
        collections_to_pass.append(
            unreal_collections.get_unreal_collection_from_unreal_collection_path(
                collection_path
            )
        )
    unreal_collections.add_collections_to_mod_entry(
        collections_to_pass, mod_name, settings_json
    )


command_help = "Remove collections to the mod entry in the settings json"


@cli.command(
    name="remove_collections_from_mod_entry", help=command_help, short_help=command_help
)
@click.option(
    "--settings_json",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the settings json, who's mod entry you want to remove collections from.",
    required=True,
)
@click.option(
    "--mod_name",
    type=str,
    help="The mod name of the mod entry in the settings json to remove the collection(s) from.",
    required=True,
)
@click.option(
    "--collection_paths",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to a collection to remove from the settings json, can be specified multiple times.",
    default=[],
    multiple=True,
)
def remove_collections_from_mod_entry(
    settings_json: pathlib.Path, mod_name: str, collection_paths: list[pathlib.Path]
):
    collections_to_pass = []
    for collection_path in collection_paths:
        collections_to_pass.append(
            unreal_collections.get_unreal_collection_from_unreal_collection_path(
                collection_path
            )
        )
    unreal_collections.remove_collections_from_mod_entry(
        collections_to_pass, mod_name, settings_json
    )


command_help = (
    "Adds the specified tags to the ini's MetaDataTagsForAssetRegistry= section."
)


@cli.command(
    name="add_meta_data_tags_for_asset_registry_to_unreal_ini",
    help=command_help,
    short_help=command_help,
)
@click.option(
    "--ini_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to edit.",
    required=True,
)
@click.option(
    "--tags",
    type=str,
    help="The new tags to add to the ini under the MetaDataTagsForAssetRegistry= section.",
    multiple=True,
    default=[],
)
def add_meta_data_tags_for_asset_registry_to_unreal_ini(
    ini_path: pathlib.Path, tags: list[str]
):
    unreal_inis.add_meta_data_tags_for_asset_registry_to_unreal_ini(
        ini=ini_path, tags=tags
    )


command_help = (
    "Removes the specified tags to the ini's MetaDataTagsForAssetRegistry= section."
)


@cli.command(
    name="remove_meta_data_tags_for_asset_registry_from_unreal_ini",
    help=command_help,
    short_help=command_help,
)
@click.option(
    "--ini_path",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="The path to the collection file to edit.",
    required=True,
)
@click.option(
    "--tags",
    type=str,
    help="The new tags to remove from the ini under the MetaDataTagsForAssetRegistry= section.",
    multiple=True,
    default=[],
)
def remove_meta_data_tags_for_asset_registry_from_unreal_ini(
    ini_path: pathlib.Path, tags: list[str]
):
    unreal_inis.remove_meta_data_tags_for_asset_registry_from_unreal_ini(
        ini=ini_path, tags=tags
    )


command_help = "Zip Directory Tree"


@cli.command(name="zip", help=command_help, short_help=command_help)
@click.option(
    "--directory",
    help="Path to the directory tree whose content to zip.",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    required=True,
)
@click.option(
    "--zip",
    help="Path to the output zip file.",
    type=click.Path(resolve_path=True, path_type=pathlib.Path),
    required=True,
)
def zip_directory_tree(directory, input_zip):
    file_io.zip_directory_tree(
        input_dir=directory,
        output_dir=os.path.dirname(input_zip),
        zip_name=os.path.basename(input_zip),
    )


command_help = "Unzip"


@cli.command(name="unzip", help=command_help, short_help=command_help)
@click.option(
    "--output_directory",
    help="Path to the directory to unzip the zip to.",
    type=click.Path(
        file_okay=False, dir_okay=True, resolve_path=True, path_type=pathlib.Path
    ),
    required=True,
)
@click.option(
    "--zip",
    help="Path to the zip.",
    type=click.Path(resolve_path=True, path_type=pathlib.Path),
    required=True,
)
def unzip(output_directory, input_zip):
    file_io.unzip_zip(zip_path=input_zip, output_location=output_directory)


command_help = "Move a file or directory to a new location."


@cli.command(name="move", help=command_help, short_help=command_help)
@click.option(
    "--input_path",
    help="The input path, to a directory tree or file.",
    type=click.Path(exists=True, resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--output_path",
    help="The output path, to a directory tree or file.",
    type=click.Path(resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--overwrite", is_flag=True, help="Overwrite existing files if they already exist."
)
def move(input_path, output_path, overwrite):
    file_io.move(input_path, output_path, overwrite)


command_help = "Copy a file or directory to a new location."


@cli.command(name="copy", help=command_help, short_help=command_help)
@click.option(
    "--input_path",
    help="The input path, to a directory tree or file.",
    type=click.Path(exists=True, resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--output_path",
    help="The output path, to a directory tree or file.",
    type=click.Path(resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--overwrite", is_flag=True, help="Overwrite existing files if they already exist."
)
def copy(input_path, output_path, overwrite):
    file_io.copy(input_path, output_path, overwrite=overwrite)


command_help = "Symlink a file or directory to a new location."


@cli.command(name="symlink", help=command_help, short_help=command_help)
@click.option(
    "--input_path",
    help="The input path, to a directory tree or file.",
    type=click.Path(exists=True, resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--output_path",
    help="The output path, to a directory tree or file.",
    type=click.Path(resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing files if they already exist.",
)
def symlink(input_path, output_path, overwrite):
    file_io.symlink(input_path, output_path, overwrite)


command_help = "Delete one or more files and/or directories."


@cli.command(name="delete", help=command_help, short_help=command_help)
@click.option(
    "--input_paths",
    help="The input path, to a directory tree or file to delete, can be specified multiple times.",
    type=click.Path(exists=True, resolve_path=True, path_type=pathlib.Path),
    required=True,
    multiple=True,
)
def delete(input_paths):
    file_io.delete(input_paths)


command_help_add_json = "Add an entry to a JSON file."


@cli.command(
    name="add_to_json", help=command_help_add_json, short_help=command_help_add_json
)
@click.option(
    "--json_path",
    help="Path to the JSON file.",
    type=click.Path(exists=True, resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option("--key", help="Key to add to the JSON file.", type=str, required=True)
@click.option(
    "--value", help="Value to associate with the key.", type=str, required=True
)
def add_to_json(json_path, key, value):
    with json_path.open("r+") as f:
        data = json.load(f)
        data[key] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    logger.log_message(f"Added {key}: {value} to {json_path}.")


command_help_remove_json = "Remove an entry from a JSON file."


@cli.command(
    name="remove_from_json",
    help=command_help_remove_json,
    short_help=command_help_remove_json,
)
@click.option(
    "--json_path",
    help="Path to the JSON file.",
    type=click.Path(exists=True, resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--key", help="Key to remove from the JSON file.", type=str, required=True
)
def remove_from_json(json_path, key):
    with json_path.open("r+") as f:
        data = json.load(f)
        if key in data:
            del data[key]
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            logger.log_message(f"Removed {key} from {json_path}.")
        else:
            logger.log_message(f"Key {key} not found in {json_path}.")


command_help_add_toml = "Add an entry to a TOML file."


@cli.command(
    name="add_to_toml", help=command_help_add_toml, short_help=command_help_add_toml
)
@click.option(
    "--toml_path",
    help="Path to the TOML file.",
    type=click.Path(exists=True, resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option("--key", help="Key to add to the TOML file.", type=str, required=True)
@click.option(
    "--value", help="Value to associate with the key.", type=str, required=True
)
def add_to_toml(toml_path, key, value):
    with toml_path.open("r+") as f:
        data = tomlkit.load(f)
        data[key] = value
        f.seek(0)
        f.write(tomlkit.dumps(data))
        f.truncate()
    logger.log_message(f"Added {key}: {value} to {toml_path}.")


command_help_remove_toml = "Remove an entry from a TOML file."


@cli.command(
    name="remove_from_toml",
    help=command_help_remove_toml,
    short_help=command_help_remove_toml,
)
@click.option(
    "--toml_path",
    help="Path to the TOML file.",
    type=click.Path(exists=True, resolve_path=True, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--key", help="Key to remove from the TOML file.", type=str, required=True
)
def remove_from_toml(toml_path, key):
    with toml_path.open("r+") as f:
        data = tomlkit.load(f)
        if key in data:
            del data[key]
            f.seek(0)
            f.write(tomlkit.dumps(data))
            f.truncate()
            logger.log_message(f"Removed {key} from {toml_path}.")
        else:
            logger.log_message(f"Key {key} not found in {toml_path}.")
