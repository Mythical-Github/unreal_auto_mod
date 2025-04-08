@echo off


cd %~dp0

taskkill /f /im "unreal_auto_mod.exe" > nul 2>&1

set exe_file="%CD%\unreal_auto_mod.exe"
set settings_json="%CD%\default\settings.json"
set arg=test_mods_all
set command=%exe_file% %arg% --settings_json_path %settings_json%

rem echo %command%
%command%

rem pause


exit /b