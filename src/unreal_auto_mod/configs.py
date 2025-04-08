import os


def resolve_special_vars(value):
    special_vars = {
        "${workspaceFolder}": os.path.abspath(
            os.path.dirname(__file__)
        ),  # Resolves dynamically
        "${home}": os.path.expanduser("~"),  # Expands to home directory
        "${cwd}": os.getcwd(),  # Expands to current working directory
    }

    if isinstance(value, str):
        for key, replacement in special_vars.items():
            value = value.replace(key, replacement)
    return value


class DynamicSettings:
    def __init__(self, settings):
        self._settings = settings

    def __getattr__(self, item):
        value = getattr(self._settings, item, None)
        return resolve_special_vars(value)

    def __getitem__(self, item):
        value = self._settings.get(item)
        return resolve_special_vars(value)
