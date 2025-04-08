## Later Later:
- [ ] retoc commands/functionality
- [ ] repak commands/functionality
- [ ] zentools commands/functionality
- [ ] aes_dumpster commands/functionality
- [ ]
- [ ] overridable colors, ability to disable coloring/progress bars/logging
- [ ] generate project files for uproject
- [ ] uproject, uplugin, engine ini edits, for popular things, maybe also generic, default map change, game instance,
- [ ] generate uproject from win 64 exe, will need the unreal engine version
- [ ] unpack/repack game/mods
- [ ] list game/mod contents
- [ ]
- [ ] linux support
- [ ] logic for mod making to scan collection contentsEE


cli commands/new launch json entries:
        - [ ] get unreal engine version, uses patternsleuth
        - [ ] get aes key, uses patternsleuth, or aesdumpster
        - [ ] get uproject name

init command, interactive, makes configs and stuff
add to path upon install from install sources
make install sources

## Later Later Later:
- [ ] automate installing from egs
- [ ] interactive wrappers
- [ ] Mod Conflict Checker
- [ ] diff game and file list, and backup diff, so later on can cleanup game list and restore from backup
- [ ] cli help replies and such are not colorized like the rest of the program, fix this
- [ ] compile all blueprints commandlet usage, maybe somehow setup for any commandlets
- [ ] layout support command
- [ ] Engine pak making compression variants (different types, in one run), defaults to compressed currently, can only do one type in one run right now
- [ ] Switch to `pathlib` from strings
- [ ] compatible game list, more for less techy people, since the tool works on virtually all games



automate asset import for meshes/skeletons/textures/physics assets, pal/da, etc.... and various properties

cli commands/new launch json entries:
        - [ ] dump usmappings

check hatch, uv, ruff, pyinstaller, etc... for inspiration and patterns
