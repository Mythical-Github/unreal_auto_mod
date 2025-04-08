import os
import sys

if sys.platform == "win32":
    import winreg


def get_epic_launcher_exe_location():
    if sys.platform != "win32":
        invalid_os_error = (
            "Epic Games Launcher path retrieval is only supported on Windows."
        )
        raise RuntimeError(invalid_os_error)

    first_arg = winreg.HKEY_LOCAL_MACHINE
    second_arg = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    reg_key = winreg.OpenKey(
        first_arg, second_arg, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY
    )

    for i in range(winreg.QueryInfoKey(reg_key)[0]):
        sub_key_name = winreg.EnumKey(reg_key, i)
        sub_key = winreg.OpenKey(reg_key, sub_key_name)
        try:
            display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
            if "Epic Games Launcher" in display_name:
                install_path, _ = winreg.QueryValueEx(sub_key, "InstallLocation")
                return os.path.join(
                    install_path, "Portal", "Binaries", "Win32", "EpicGamesLauncher.exe"
                )
        except FileNotFoundError:
            pass
        finally:
            winreg.CloseKey(sub_key)
    winreg.CloseKey(reg_key)
    return "Epic Games Launcher installation not found in the registry."
