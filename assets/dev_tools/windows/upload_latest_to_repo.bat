@echo off

cd /d %~dp0

set "repo_branch=dev"

set "py_project_dev_tools_exe=%CD%\..\py_project_dev_tools.exe"

set "toml=%CD%\..\..\..\pyproject.toml"

"%py_project_dev_tools_exe%" upload_latest_to_repo --project_toml_path "%toml%" --repo_branch %repo_branch%

exit /b 0
