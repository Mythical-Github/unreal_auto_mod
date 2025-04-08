from enum import Enum


class PackingType(Enum):
    """
    enum for how to treat packing mods
    """
    ENGINE = 'engine'
    UNREAL_PAK = 'unreal_pak'
    REPAK = 'repak'
    LOOSE = 'loose'


class GameLaunchType(Enum):
    """
    enum for how to launch the game
    """
    EXE = 'exe'
    STEAM = 'steam'
    EPIC = 'epic'
    ITCH_IO = 'itch_io'
    BATTLE_NET = 'battle_net'
    ORIGIN = 'origin'
    UBISOFT = 'ubisoft'
    OTHER = 'other'


class ScriptStateType(Enum):
    """
    enum for the various script states, used to fire off other functions
    at specific times
    """
    NONE = 'none'
    PRE_ALL = 'pre_all'
    POST_ALL = 'post_all'
    CONSTANT = 'constant'
    PRE_INIT = 'pre_init'
    INIT = 'init'
    POST_INIT = 'post_init'
    PRE_COOKING = 'pre_cooking'
    POST_COOKING = 'post_cooking'
    PRE_MODS_UNINSTALL = 'pre_mods_uninstall'
    POST_MODS_UNINSTALL = 'post_mods_uninstall'
    PRE_PAK_DIR_SETUP = 'pre_pak_dir_setup'
    POST_PAK_DIR_SETUP = 'post_pak_dir_setup'
    PRE_MODS_INSTALL = 'pre_mods_install'
    POST_MODS_INSTALL = 'post_mods_install'
    PRE_GAME_LAUNCH = 'pre_game_launch'
    POST_GAME_LAUNCH = 'post_game_launch'
    PRE_GAME_CLOSE = 'pre_game_close'
    POST_GAME_CLOSE = 'post_game_close'
    PRE_ENGINE_OPEN = 'pre_engine_open'
    POST_ENGINE_OPEN = 'post_engine_open'
    PRE_ENGINE_CLOSE = 'pre_engine_close'
    POST_ENGINE_CLOSE = 'post_engine_close'


class ExecutionMode(Enum):
    """
    enum for how to execute various processes
    """
    SYNC = 'sync'
    ASYNC = 'async'


class CompressionType(Enum):
    """
    enum for the types of mod pak compression
    """
    NONE = 'None'
    ZLIB = 'Zlib'
    GZIP = 'Gzip'
    OODLE = 'Oodle'
    ZSTD = 'Zstd'
    LZ4 = 'Lz4'
    LZMA = 'Lzma'


class UnrealModTreeType(Enum):
    """
    enum for the mod dir type in the unreal file system
    there are two main conventions used by communities
    """
    CUSTOM_CONTENT = 'CustomContent'  # "Content/CustomContent/ModName"
    MODS = 'Mods'  # "Content/Mods/ModName"


class FileFilterType(Enum):
    """
    enum for how to include various files for mod creation functions
    """
    ASSET_PATHS = 'asset_paths'  # Takes the paths and gets all files regardless of extension
    TREE_PATHS = 'tree_paths'  # Takes supplied dirs, and traverses it all, including every file


def get_enum_from_val(enum: Enum, value: str) -> Enum:
    """
    """
    for member in enum:
        if member.value == value:
            return member
    return None
