@echo off

cd /d %~dp0

set "project_directory=%CD%"
set "content_zip_urls=https://github.com/Mythical-Github/py_project_dev_tools/releases/latest/download/py_project_dev_tools.zip"
set "project_updater_exe=%CD%\dev_tools_updater\project_updater.exe"

set "command=update_project --project_directory "%project_directory%" --content_zip_urls "%content_zip_urls%" --backup_exclusions logs dev_tools_updater update_dev_tools.bat"

"%project_updater_exe%" %command%

exit /b 0