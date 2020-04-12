#! /usr/bin/env python3


import os
import re
import sys
import argparse
from subprocess import run


def project_environment_variables(file_path):
    key_value_regex = re.compile(r"^(?P<key>\w+)=(?P<value>[\S]*)$")
    environment = {}

    with open(file_path) as environment_file:
        for line in environment_file:
            matches = key_value_regex.match(line)

            if matches is not None:
                matches = matches.groupdict()
                environment[matches["key"]] = matches["value"]

    return environment


if __name__ == "__main__":
    env = project_environment_variables(".env")

    parser = argparse.ArgumentParser(
        description=f"Perform common tasks on the {env['PROJECT_NAME']} application stack.")

    parser.add_argument("tool",
                        help="Define a tool to use on the application stack.",
                        choices=("artisan", "composer", "yarn", "phpunit"))
    parser.add_argument("arguments",
                        nargs=argparse.REMAINDER,
                        help="Optional arguments to pass to the specified tool.")

    parsed = parser.parse_args()

    if parsed.tool == "artisan":
        run(["docker-compose", "exec", "--user", "www-data", "php", "php", "artisan"] + parsed.arguments)

    elif parsed.tool == "composer":
        run(["docker", "run",
             "--rm",
             "--interactive",
             "--tty",
             "--user", f"{env['USER_ID']}:{env['GROUP_ID']}",
             "--workdir", "/application",
             "--mount", f"type=bind,source={os.getcwd()}/application/{env['PROJECT_NAME']},target=/application",
             f"composer:{env['COMPOSER_IMAGE_TAG']}"] + parsed.arguments)

    elif parsed.tool == "yarn":
        run(["docker", "run",
             "--rm",
             "--interactive",
             "--tty",
             "--user", f"{env['USER_ID']}:{env['GROUP_ID']}",
             "--workdir", "/application",
             "--mount", f"type=bind,source={os.getcwd()}/application/{env['PROJECT_NAME']},target=/application",
             f"node:{env['NODE_IMAGE_TAG']}", "yarn"] + parsed.arguments)

    elif parsed.tool == "phpunit":
        run(["docker-compose", "exec", "--user", "www-data", "php", "php", "./vendor/bin/phpunit"] + parsed.arguments)

    else:
        parser.print_help()
        sys.exit(1)
