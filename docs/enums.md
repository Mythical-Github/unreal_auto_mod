## Enums Documentation

### WindowAction

Enum for handling window actions.

- **NONE**: 'none'
- **MIN**: 'min'
- **MAX**: 'max'
- **MOVE**: 'move'
- **CLOSE**: 'close'

### PackingType

Enum for how to pack mods.

- **ENGINE**: 'engine'
- **UNREAL_PAK**: 'unreal_pak'
- **REPAK**: 'repak'
- **LOOSE**: 'loose'

### GameLaunchType

Enum for how to launch the game.

- **EXE**: 'exe'
- **STEAM**: 'steam'
- **EPIC**: 'epic'
- **ITCH_IO**: 'itch_io'
- **BATTLE_NET**: 'battle_net'
- **ORIGIN**: 'origin'
- **UBISOFT**: 'ubisoft'
- **OTHER**: 'other'

### ScriptStateType

Enum for the various script states, used to fire off other functions at specific times.

- **NONE**: 'none'
- **PRE_ALL**: 'pre_all'
- **POST_ALL**: 'post_all'
- **CONSTANT**: 'constant'
- **PRE_INIT**: 'pre_init'
- **INIT**: 'init'
- **POST_INIT**: 'post_init'
- **PRE_COOKING**: 'pre_cooking'
- **POST_COOKING**: 'post_cooking'
- **PRE_MODS_UNINSTALL**: 'pre_mods_uninstall'
- **POST_MODS_UNINSTALL**: 'post_mods_uninstall'
- **PRE_PAK_DIR_SETUP**: 'pre_pak_dir_setup'
- **POST_PAK_DIR_SETUP**: 'post_pak_dir_setup'
- **PRE_MODS_INSTALL**: 'pre_mods_install'
- **POST_MODS_INSTALL**: 'post_mods_install'
- **PRE_GAME_LAUNCH**: 'pre_game_launch'
- **POST_GAME_LAUNCH**: 'post_game_launch'
- **PRE_GAME_CLOSE**: 'pre_game_close'
- **POST_GAME_CLOSE**: 'post_game_close'
- **PRE_ENGINE_OPEN**: 'pre_engine_open'
- **POST_ENGINE_OPEN**: 'post_engine_open'
- **PRE_ENGINE_CLOSE**: 'pre_engine_close'
- **POST_ENGINE_CLOSE**: 'post_engine_close'

### ExecutionMode

Enum for how to execute various processes.

- **SYNC**: 'sync'
- **ASYNC**: 'async'

### CompressionType

Enum for the types of mod pak compression.

- **NONE**: 'None'
- **ZLIB**: 'Zlib'
- **GZIP**: 'Gzip'
- **OODLE**: 'Oodle'
- **ZSTD**: 'Zstd'
- **LZ4**: 'Lz4'
- **LZMA**: 'Lzma'

### UnrealModTreeType

Enum for the mod dir type in the Unreal file system.
There are two main conventions used by communities.

- **CUSTOM_CONTENT**: 'CustomContent' // "Content/CustomContent/ModName"
- **MODS**: 'Mods' // "Content/Mods/ModName"
