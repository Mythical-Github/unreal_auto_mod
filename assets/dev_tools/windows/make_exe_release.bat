@echo off

cd /d %~dp0

set "py_project_dev_tools_exe=%CD%/..\py_project_dev_tools.exe"

set "toml=%CD%\..\..\..\pyproject.toml"

"%py_project_dev_tools_exe%" make_exe_release --project_toml_path "%toml%"

set "dist_dir=%CD%\..\..\..\dist"

start explorer "%dist_dir%"

exit /b 0
