@echo off

cd /d %~dp0

set "py_project_dev_tools_exe=%CD%\..\py_project_dev_tools.exe"

set "toml=%CD%\..\..\..\pyproject.toml"

"%py_project_dev_tools_exe%" setup_virtual_environment --project_toml_path "%toml%" --env_name "dev"

exit /b 0
