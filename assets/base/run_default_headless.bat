@echo off

cd /D %~dp0

set exe_file=%CD%\unreal_auto_mod.exe
set settings_json=%CD%\default\settings.json
set arg=test_mods_all
set command=%exe_file% %arg% --settings_json_path %settings_json%

start "" /B mshta.exe vbscript:(CreateObject("WScript.Shell").Run("cmd /c ""%command%""",0))(Window.Close)

exit /b