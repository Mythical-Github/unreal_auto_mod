#!/bin/bash

cd "$(dirname "$0")"

py_project_dev_tools_exe="$(cd .. && pwd)/py_project_dev_tools"

toml="$(cd ../../../ && pwd)/pyproject.toml"

"$py_project_dev_tools_exe" setup_virtual_environment --project_toml_path "$toml" --env_name "dev"

exit 0
