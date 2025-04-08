import argparse

from unreal_auto_mod.log_py import log_message


def cli_logic(cli_data):
    commands_module = cli_data['module']
    cli_info_dict = cli_data['commands']

    parser = argparse.ArgumentParser(description="Easy To Use Command Line Modding Utility For Unreal Engine Games 4.0-5.5")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    for command, command_info in cli_info_dict.items():
        subcommand_parser = subparsers.add_parser(command, help=f"Execute {command} command")

        arg_help_pairs = command_info.get('arg_help_pairs', [])

        for arg_entry in arg_help_pairs:
            for arg_name, arg_data in arg_entry.items():
                subcommand_parser.add_argument(
                    f"--{arg_name}",
                    type=str,
                    help=arg_data["help"],
                    required=arg_data["required"],
                    nargs="+" if arg_data["use_nargs"] else None
                )

    args = parser.parse_args()

    if args.command:
        command_info = cli_info_dict.get(args.command)
        if command_info:
            function_name = command_info['function_name']
            function = getattr(commands_module, function_name, None)
            if function:
                function_args = [
                    getattr(args, arg_name, None)
                    for arg_help_pair in command_info['arg_help_pairs']
                    for arg_name in arg_help_pair.keys()
                ]

                log_message(f"Function: {function_name} was called with args: {function_args}")
                function(*function_args)
            else:
                log_message(f"Function {function_name} not found in {commands_module}.")
        else:
            log_message("Invalid command.")
            parser.print_help()
    else:
        log_message("No command provided.")
        parser.print_help()
