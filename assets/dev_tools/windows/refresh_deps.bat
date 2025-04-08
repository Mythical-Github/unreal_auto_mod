@echo off

cd /d %~dp0

set "py_project_dev_tools_exe=%CD%\..\py_project_dev_tools.exe"

set "toml=%CD%\..\..\..\pyproject.toml"

"%py_project_dev_tools_exe%" refresh_deps --project_toml_path "%toml%"

exit /b 0
