from enum import Enum


class PackagingDirType(Enum):
    """
    enum for the directory type for packaging, it changes based on ue version
    """
    WINDOWS = 'windows'
    WINDOWS_NO_EDITOR = 'windows_no_editor'
