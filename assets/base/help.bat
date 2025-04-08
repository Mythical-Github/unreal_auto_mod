@echo off


cd %~dp0


set exe_file="%CD%\unreal_auto_mod.exe"
set arg=test_mods
set help_command_one=%exe_file%  -h
set help_command_two=%exe_file% %arg% -h

echo %help_command_one%
%help_command_one%


echo %help_command_two%
%help_command_two%


pause


exit /b