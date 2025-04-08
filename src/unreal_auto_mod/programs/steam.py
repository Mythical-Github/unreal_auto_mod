import os
import sys

if sys.platform == "win32":
    import winreg


def get_steam_exe_location():
    if sys.platform != "win32":
        steam_location_error = "Steam path retrieval is only supported on Windows."
        raise RuntimeError(steam_location_error)

    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Valve\Steam",
            0,
            winreg.KEY_READ,
        )
        install_path, _ = winreg.QueryValueEx(reg_key, "InstallPath")
        winreg.CloseKey(reg_key)
        return os.path.join(install_path, "steam.exe")
    except FileNotFoundError:
        return "Steam: installation not found in the registry."
