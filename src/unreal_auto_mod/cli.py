from unreal_auto_mod import settings

OPTIONS = {
    "module": settings,
    "commands": {
        "test_mods": {
            "function_name": "test_mods",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }},
                {"mod_names": {
                    "help": "list of mod_names, strings",
                    "required": True,
                    "use_nargs": True
                }}
            ]
        },
        "test_mods_all": {
            "function_name": "test_mods_all",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        },
        "open_latest_log": {
            "function_name": "open_latest_log",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        },
        "run_game": {
            "function_name": "run_game",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        },
        "install_uasset_gui": {
            "function_name": "open_uasset_gui",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        },
        "install_kismet_analyzer": {
            "function_name": "open_kismet_analyzer",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        },
        "install_stove": {
            "function_name": "open_stove",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        },
        "install_umodel": {
            "function_name": "open_umodel",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        },
        "install_fmodel": {
            "function_name": "open_fmodel",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        },
        "install_spaghetti": {
            "function_name": "open_spaghetti",
            "arg_help_pairs": [
                {"settings_json_path": {
                    "help": "Path to settings.json",
                    "required": True,
                    "use_nargs": False
                }}
            ]
        }
    }
}
