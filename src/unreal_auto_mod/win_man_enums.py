from enum import Enum


class WindowAction(Enum):
    """
    enum for how to treat handling windows
    """
    NONE = 'none'
    MIN = 'min'
    MAX = 'max'
    MOVE = 'move'
    CLOSE = 'close'
