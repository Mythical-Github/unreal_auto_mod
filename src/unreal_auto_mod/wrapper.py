import os
import sys

from unreal_auto_mod import file_io


def get_wrapper_location() -> str:
    return os.path.normpath(
        f"{file_io.SCRIPT_DIR}/dist/command.{file_io.get_platform_wrapper_extension()}"
    )


def generate_wrapper():
    args = sys.argv[:]

    if "--wrapper_name" in args:
        index = args.index("--wrapper_name")
        args.pop(index)
        args.pop(index)

    if not os.path.isabs(args[0]):
        args[0] = f'"{os.path.join(file_io.SCRIPT_DIR, args[0])}"'

    content = " ".join(args)

    wrapper_path = get_wrapper_location()

    os.makedirs(os.path.dirname(wrapper_path), exist_ok=True)

    with open(wrapper_path, "w") as f:
        f.write(content)
