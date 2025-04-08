## Settings Json Documentation

## General Info

- **Override Default Working Directory**:
    - **Description**: Specifies if you want the folder that gets turned into paks to be in a specific place. Defaults
      to next to the exe/py.
    - **Value**: `false` (true/false)
- **Working Directory**:
    - **Description**: Directory for the override if used.
    - **Value**: `"C:/Users/Mythical/Downloads/Output"`
- **Window Title**:
    - **Description**: Title for the script window, useful for the auto move windows section.
    - **Value**: `"UnrealAutoMod Automation Script"`

## Engine Info

- **Unreal Engine Directory**:
    - **Description**: Path to the Unreal Engine installation directory.
    - **Value**: `"D:/unreal_engine_installs/UE_4.22"`
- **Unreal Project File**:
    - **Description**: Path to the Unreal project file (.uproject).
    - **Value**: `"C:/Users/Mythical/Documents/Github/InterposePrivate/unreal_project/Interpose/KevinSpel.uproject"`
- **Toggle Engine During Testing**:
    - **Description**: Whether to toggle the engine on and off during testing.
    - **Value**: `false` (true/false)
- **Resave Packages and Fix Up Redirectors Before Engine Open**:
    - **Description**: Whether to resave packages and fix up redirectors before opening the engine.
    - **Value**: `true` (true/false)
- **Engine Launch Args**:
    - **Description**: Additional arguments for engine launch.
    - **Value**: `[]`
- **Engine Cook and Packaging Args**:
    - **Description**: Additional arguments for cooking and packaging.
    - **Value**: `[]`
- **Use Unversioned Cooked Content**:
    - **Description**: Use unversioned cooked content.
    - **Value**: `true` (true/false)
- **Clear .uproject Saved Cooked Directory Before Tests**:
    - **Description**: Clear the saved cooked directory before tests.
    - **Value**: `false` (true/false)
- **Always Build Project**:
    - **Description**: Always build the project.
    - **Value**: `false` (true/false)
- **Override Automatic Version Finding**:
    - **Description**: Override the automatic version finding.
    - **Value**: `false` (true/false)
- **Unreal Engine Major Version**:
    - **Description**: Major version of the Unreal Engine.
    - **Value**: `"4"`
- **Unreal Engine Minor Version**:
    - **Description**: Minor version of the Unreal Engine.
    - **Value**: `"22"`

## Game Info

- **Game Executable Path**:
    - **Description**: Path to the game executable.
    - **Value**: `"D:/SteamLibrary/steamapps/common/Zedfest/KevinSpel/Binaries/Win64/Zedfest.exe"`
- **Launch Type**:
    - **Description**: `can be any of the GameLaunchType enums`
    - **Value**: `"steam"`
- **Override Automatic Launcher Executable Finding**:
    - **Description**: Override the automatic finding of the launcher executable.
    - **Value**: `false` (true/false)
- **Game Launcher Executable**:
    - **Description**: Path to the game launcher executable.
    - **Value**: `"C:/Program Files (x86)/Steam/steam.exe"`
- **Game ID**:
    - **Description**: Steam game ID.
    - **Value**: `1037080`
- **Skip Launching Game**:
    - **Description**: Skip launching the game.
    - **Value**: `false` (true/false)
- **Override Automatic Window Title Finding**:
    - **Description**: Override the automatic window title finding.
    - **Value**: `false` (true/false)
- **Window Title Override String**:
    - **Description**: String to override window title.
    - **Value**: `"Zedfest"`
- **Launch Params**:
    - **Description**: Additional launch parameters.
    - **Value**: `[
      "-fileopenlog",
      "-NOSPLASH"
      ]`

## Alternative .uproject Name in Game Directory

- **Use Alternative Method**:
    - **Description**: Use an alternative method for .uproject naming.
    - **Value**: `false` (true/false)
- **Name**:
    - **Description**: Alternative name for .uproject.
    - **Value**: `"Game"`

## Repak Info

- **Repak Path**:
    - **Description**: Path to the Repak executable.
    - **Value**: `"C:/modding/unreal_engine/repak/repak.exe"`
- **Override Automatic Version Finding**:
    - **Description**: Override automatic version finding.
    - **Value**: `false` (true/false)
- **Repak Version**:
    - **Description**: Version of Repak.
    - **Value**: `"V11"`

## Alternative Executable Methods

- **Example Entry**:
    - **Script State**: `pre_game_launch`: `can be any of the ScriptStateType enums`
    - **Alternative Executable Path**: `"C:/modding/unreal_engine/Umodel/umodel.exe"`
    - **Execution Mode**: `async`: `can be any of the UnrealModTreeType enums`
    - **Variable Args**: `[]`

## Process Kill Info

- **Auto Close Game**:
    - **Description**: Automatically close the game.
    - **Value**: `true` (true/false)
- **Processes to Kill**:
    - **Process Name**: `"Fmodel.exe"`
    - **Use Substring Check**: `false` (true/false)
    - **Script State**: `all`: `can be any of the ScriptStateType enums`

## Auto Move Windows

- **Window Name**: `"UE4SS"`
    - **Use Substring Check**: `true` (true/false)
    - **Window Behaviour**: `move`: `can be any of the WindowAction enums`
    - **Script State**: `post_game_launch`: `can be any of the ScriptStateType enums`
    - **Monitor**: `1`
    - **Resolution**:
        - **X**: `1525`
        - **Y**: `850`

## Mod Pak Info

- **Mod Name**: `"EnginePakExample_P"`
    - **Pak Directory Structure**: `"LogicMods"`
    - **Mod Name Directory Type**: `"Mods"`: `can be any of the UnrealModTreeType enums`
    - **Use Mod Name Directory Name Override**: `false` (true/false)
    - **Mod Name Directory Name Override**: `null`
    - **Pak Chunk Number**: `1`
    - **Packing Type**: `"engine"`: `can be any of the PackingType enums`
    - **Compression Type**: `"None"`: `can be any of the CompressionType enums`
    - **Is Enabled**: `false` (true/false)
    - **Manually Specified Assets**:
        - **Asset Paths**: `[]`
        - **Tree Paths**: `[]`
