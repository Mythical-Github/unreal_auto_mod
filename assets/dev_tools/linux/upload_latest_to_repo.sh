#!/bin/bash

cd "$(dirname "$0")"

repo_branch="dev"

py_project_dev_tools_exe="$(cd .. && pwd)/py_project_dev_tools"

toml="$(cd ../../../ && pwd)/pyproject.toml"

"$py_project_dev_tools_exe" upload_latest_to_repo --project_toml_path "$toml" --repo_branch "$repo_branch"

exit 0
