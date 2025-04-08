from enum import Enum
from typing import Type, Any


class PackingType(Enum):
    """
    enum for how to treat packing mods
    """

    ENGINE = "engine"
    UNREAL_PAK = "unreal_pak"
    REPAK = "repak"
    LOOSE = "loose"


class GameLaunchType(Enum):
    """
    enum for how to launch the game
    """

    EXE = "exe"
    STEAM = "steam"
    EPIC = "epic"
    ITCH_IO = "itch_io"
    BATTLE_NET = "battle_net"
    ORIGIN = "origin"
    UBISOFT = "ubisoft"
    OTHER = "other"


class HookStateType(Enum):
    """
    enum for the various hook states, used to fire off other functions
    at specific times, constant and init are not for use with the hook_state_decorator
    """

    CONSTANT = "constant"
    INIT = "init"

    PRE_ALL = "pre_all"
    POST_ALL = "post_all"
    PRE_INIT = "pre_init"
    POST_INIT = "post_init"
    PRE_COOKING = "pre_cooking"
    POST_COOKING = "post_cooking"
    PRE_MODS_UNINSTALL = "pre_mods_uninstall"
    POST_MODS_UNINSTALL = "post_mods_uninstall"
    PRE_PAK_DIR_SETUP = "pre_pak_dir_setup"
    POST_PAK_DIR_SETUP = "post_pak_dir_setup"
    PRE_MODS_INSTALL = "pre_mods_install"
    POST_MODS_INSTALL = "post_mods_install"
    PRE_GAME_LAUNCH = "pre_game_launch"
    POST_GAME_LAUNCH = "post_game_launch"
    PRE_GAME_CLOSE = "pre_game_close"
    POST_GAME_CLOSE = "post_game_close"
    PRE_ENGINE_OPEN = "pre_engine_open"
    POST_ENGINE_OPEN = "post_engine_open"
    PRE_ENGINE_CLOSE = "pre_engine_close"
    POST_ENGINE_CLOSE = "post_engine_close"
    PRE_CLEANUP = "pre_cleanup"
    POST_CLEANUP = "post_cleanup"
    PRE_CHANGES_UPLOAD = "pre_changes_upload"
    POST_CHANGES_UPLOAD = "post_changes_upload"
    PRE_BUILD_UPROJECT = "pre_uproject_build"
    POST_BUILD_UPROJECT = "post_uproject_build"
    PRE_GENERATE_MOD_RELEASE = "pre_generate_mod_release"
    POST_GENERATE_MOD_RELEASE = "post_generate_mod_release"
    PRE_GENERATE_MOD_RELEASES = "pre_generate_mod_releases"
    POST_GENERATE_MOD_RELEASES = "post_generate_mod_releases"
    PRE_GENERATE_MOD = "pre_generate_mod"
    POST_GENERATE_MOD = "post_generate_mod"
    PRE_GENERATE_MODS = "pre_generate_mods"
    POST_GENERATE_MODS = "post_generate_mods"


class ExecutionMode(Enum):
    """
    enum for how to execute various processes
    """

    SYNC = "sync"
    ASYNC = "async"


class CompressionType(Enum):
    """
    enum for the types of mod pak compression
    """

    NONE = "None"
    ZLIB = "Zlib"
    GZIP = "Gzip"
    OODLE = "Oodle"
    ZSTD = "Zstd"
    LZ4 = "Lz4"
    LZMA = "Lzma"


class UnrealModTreeType(Enum):
    """
    enum for the mod dir type in the unreal file system
    there are two main conventions used by communities
    """

    CUSTOM_CONTENT = "CustomContent"  # "Content/CustomContent/ModName"
    MODS = "Mods"  # "Content/Mods/ModName"


class FileFilterType(Enum):
    """
    enum for how to include various files for mod creation functions
    """

    ASSET_PATHS = (
        "asset_paths"  # Takes the paths and gets all files regardless of extension
    )
    TREE_PATHS = (
        "tree_paths"  # Takes supplied dirs, and traverses it all, including every file
    )


class WindowAction(Enum):
    """
    enum for how to treat handling windows
    """

    NONE = "none"
    MIN = "min"
    MAX = "max"
    MOVE = "move"
    CLOSE = "close"


class PackagingDirType(Enum):
    """
    enum for the directory type for packaging, it changes based on ue version
    """

    WINDOWS = "windows"
    WINDOWS_NO_EDITOR = "windows_no_editor"


class UnrealHostTypes(Enum):
    """
    enum for the unreal host types, for descriptor files
    """

    RUNTIME = "runtime"
    RUNTIME_NO_COMMANDLET = "runtime_no_commandlet"
    RUNTIME_AND_PROGRAM = "runtime_and_program"
    COOKED_ONLY = "cooked_only"
    UNCOOKED_ONLY = "uncooked_only"
    DEVELOPER = "developer"
    DEVELOPER_TOOL = "developer_tool"
    EDITOR = "editor"
    EDITOR_NO_COMMANDLET = "editor_no_commandlet"
    EDITOR_AND_PROGRAM = "editor_and_program"
    PROGRAM = "program"
    SERVER_ONLY = "server_only"
    CLIENT_ONLY = "client_only"
    CLIENT_ONLY_NO_COMMANDLET = "client_only_no_commandlet"
    MAX = "max"


class LoadingPhases(Enum):
    """
    Enum for the loading phases, for descriptor files
    """

    EARLIEST_POSSIBLE = "earliest_possible"
    POST_CONFIG_INIT = "post_config_init"
    POST_SPLASH_SCREEN = "post_splash_screen"
    PRE_EARLY_LOADING_SCREEN = "pre_early_loading_screen"
    PRE_LOADING_SCREEN = "pre_loading_screen"
    PRE_DEFAULT = "pre_default"
    DEFAULT = "default"
    POST_DEFAULT = "post_default"
    POST_ENGINE_INIT = "post_engine_init"
    NONE = "none"
    MAX = "max"


class UnrealIostoreFileExtensions(Enum):
    """
    Enum for the file extensions for files that should end up in iostore utoc and ucas files
    If creating an iostore mod all files with extensions not within this list's corresponding string values
    will be assumed to be pak assets
    """

    UMAP = "umap"
    UEXP = "uexp"
    UPTNL = "uptnl"
    UBULK = "ubulk"
    UASSET = "uasset"
    USHADERBYTECODE = "ushaderbytecode"


class SigMethodType(Enum):
    """
    Enum for the way to provide a sig when creating a mod release
    """

    NONE = "none"  # doesn't generate one
    COPY = "copy"  # copies and renames an existing one from the game install
    EMPTY = (
        "empty"  # creates an empty file named and placed where the actual sig should be
    )


def get_enum_from_val(enum_cls: Type[Enum], value: Any) -> Enum:
    for entry in enum_cls:
        if entry.value == value:
            return entry
    raise ValueError(f"{value} is not a valid value for {enum_cls.__name__}")


def get_enum_strings_from_enum(enum_cls: Type[Enum]) -> list[str]:
    return [entry.value for entry in enum_cls]
