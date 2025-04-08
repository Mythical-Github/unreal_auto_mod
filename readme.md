<h1 id="title" align="left">UnrealAutoMod</h1>

Easy To Use Command Line Modding Utility For Unreal Engine Games 4.0-5.5 <br>
Automates creation, and placement, of mod archives, and other various actions. <br>
For an in editor menu version check out [UnrealAutoModInEditor](https://github.com/Mythical-Github/UnrealAutoModInEditor)

<h2>Project Example:</h2>

[![Project Screenshot](https://github.com/Mythical-Github/UnrealAutoMod/assets/4b65e3a3-ae7f-4881-bea4-e73191594587.png)](https://github.com/user-attachments/assets/76da1afc-9c30-4ec8-b27c-8c072e73f696)


<h2 id="features">💪 Features</h2>

* Supports Unreal Engine versions: 4.0-5.5
* Supports loose file modding (unreal assets, not in a mod archive, like a .pak)
* Supports modding iostore games
* Automatic mod creation and placement
* Automatic engine cooking, and packaging
* Automatic game running
* Automatic editor running
* Event management system
* Process management events
* Window management events
* Automatic script/exec running events
* Supports creation of mod archives, through unreal_pak, repak, and engine made archives
* Ability to add launch params to various script/exec running
* Supports games with alternative packing structures (example game: Kingdom Hearts 3)
* Supports packing edited files, through the persistent_files dir, or through the Event Management System
* Easily configure what files end up in your final mod(s) and how with the Mod list within the config
* Supports loading from json file, so you can have multiple projects easily
* Logging
* Colorful printouts
* Ability to run in the background, with no windows


<h2 id="installation_steps">🛠️ Installation Steps:</h2>

1. Download and unzip the latest [release](https://github.com/Mythical-Github/UnrealAutoMod/releases/latest).\
You can keep the program anywhere you'd like.

### 2. **Configure the Default JSON File**

Most users will only need to edit a few settings, which can be done with a text editor. In the JSON file, you typically need to update the following:

- **Unreal Engine `.uproject` File Path**  
  Specify the path to your Unreal Engine project file.

- **Unreal Engine Directory**  
  Define the directory where Unreal Engine is installed.

- **Game's Win64 Executable Path**  
  Set the path to the game's Win64 executable. Ensure that the path is valid:
  - **Correct Example:**  
    `"D:\SteamLibrary\steamapps\common\Zedfest\KevinSpel\Binaries\Win64\Zedfest.exe"`
  - **Incorrect Example:**  
    `"D:\SteamLibrary\steamapps\common\Zedfest\KevinSpel.exe"`

- **Steam App ID**  
  If using the Steam launch method (as opposed to the executable method), enter the Steam App ID.

- **Window Title Override String**  
  Specify the string for the launched game's window label.

After configuring these settings, you can proceed to configure the mod list.

###
3. **Configure the mod list:**  
   You can include any number of mod entries in the list.
  

  ```
   {
      {
      "mod_name": "MapKit",
      "pak_dir_structure": "~mods",
      "mod_name_dir_type": "Mods",
      "use_mod_name_dir_name_override": false,
      "mod_name_dir_name_override": null,
      "pak_chunk_num": null,
      "packing_type": "repak",
      "compression_type": "Zlib",
      "is_enabled": true,
      "manually_specified_assets": {
        "asset_paths": [],
        "tree_paths": []
      }
    },
    {
      "mod_name": "ExampleLevel",
      "pak_dir_structure": "~mods",
      "mod_name_dir_type": "Mods",
      "use_mod_name_dir_name_override": false,
      "mod_name_dir_name_override": null,
      "pak_chunk_num": null,
      "packing_type": "repak",
      "compression_type": "Zlib",
      "is_enabled": true,
      "manually_specified_assets": {
        "asset_paths": [],
        "tree_paths": []
      }
    }
  ```

### Configuration Details

- **`mod_name`**: This will be the final mod archive's file name, e.g., `mod_name.pak`.

- **`pak_dir_structure`**: Specifies the folder structure within the game's `Content/Paks/` directory. Common values are `~mods` and `LogicMods`.

- **`mod_name_dir_type`**: Determines the built-in auto-include directory.
  - `Mods` will include files from `Game/Mods/ModName/`.
  - `CustomContent` will include files from `Game/CustomContent/ModName/`.

- **`use_mod_name_dir_name_override`**: Set to `true` if you want your final mod name to include a suffix (e.g., `_P`), but not the internal project name. Example: `Content/Paks/~mods/ExampleName_P` vs. `Game/Mods/ExampleName`.

- **`mod_name_dir_name_override`**: Specifies the folder to use instead of the default. Usually the `mod_name` without any suffix.

- **`pak_chunk_num`**: Used only if you are using the engine packing enum. Set this to match what you configured inside Unreal Engine.

- **`packing_type`**: Specifies the packing method:
  - `repak` for general use.
  - `engine` for iostore games.
  - `loose` for games using loose file modding.
  - `unreal_pak` for when you want to pak using unreal_pak, from your game engine install, usually not ever needed.

- **`compression_type`**: Determines the compression method for the mod archives. Not applicable for loose file modding.

- **`is_enabled`**: Set to `false` to disable packaging of the mod and uninstall it if it exists in the specified mod directory.

- **`manually_specified_assets`**: Lists additional assets to include:
  - **`asset_paths`**: Direct paths to specific files (e.g., `test.uasset`, `test.uexp`).
  - **`tree_paths`**: Include all files in subfolders within specified directories.

### Additional Notes

- For JSON paths, use forward slashes (`/`) instead of backslashes (`\`). Make sure your paths match this format when editing the JSON file.
- [Settings Json Reference](https://github.com/Mythical-Github/UnrealAutoMod/blob/main/docs/settings_json.md)
- [Faq](https://github.com/Mythical-Github/UnrealAutoMod/blob/main/docs/faq.md)

###

4. **Run the application:**  
   Once everything is set up, you can proceed to the [Running Steps](#running-steps).

<h2 id="running-steps">🏃 Running Steps:</h2>
The release version, has some included bat files.<br>
You can use these to run the default config, with the test_mods_all arg, or use it as a base and edit it.
There is also a version to run it headless (windowless).

The program itself, supports various command line parameters.
Here are some examples of how you would use it.

```
unreal_auto_mod.exe -h
```

```
unreal_auto_mod.exe command -h
```

```
unreal_auto_mod.exe test_mods_all --settings_json_path <settings_json_path>
```

```
unreal_auto_mod.exe settings.json test_mods --settings_json_path <settings_json_path> --mod_names [<mod_name> ...]
```

<h2>💻 References</h2>

* [Faq](https://github.com/Mythical-Github/UnrealAutoMod/blob/main/docs/faq.md)
* [Enums Reference](https://github.com/Mythical-Github/UnrealAutoMod/blob/main/docs/enums.md)
* [Settings Json Reference](https://github.com/Mythical-Github/UnrealAutoMod/blob/main/docs/settings_json.md)
* [Youtube Example Setup Reference](https://www.youtube.com/watch?v=6MUkUFhumo8)

<h2>💻 Built with</h2>

* Python

<h2>🛡️ License:</h2>

[![license](https://www.gnu.org/graphics/gplv3-with-text-136x68.png)](LICENSE)
