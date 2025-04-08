@echo off

cd /d %~dp0

set "project_directory=%CD%"
set "content_zip_urls=https://github.com/Mythical-Github/unreal_auto_mod/releases/latest/download/unreal_auto_mod.zip"
set "project_updater_exe=%CD%\project_updater\project_updater.exe"

set "command=update_project --project_directory "%project_directory%" --content_zip_urls "%content_zip_urls%" --backup_exclusions project_updater unreal_auto_mod_updater.bat"

"%project_updater_exe%" %command%

exit /b 0