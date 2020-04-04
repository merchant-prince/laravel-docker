#! /usr/bin/env python3


import os
import sys
import argparse
from subprocess import run




def get_project_environment_variables(file_path):
    environment = {}

    with open(file_path) as environment_file:
        for line in environment_file:
            key, value = [word.strip() for word in line.split("=", 1)]
            environment[key] = value

    return environment




if __name__ == "__main__":
    env = get_project_environment_variables(".env")

    parser = argparse.ArgumentParser(description = f"Perform common tasks on the {env['PROJECT_NAME']} application stack.")

    parser.add_argument("tool", help="Define a tool to use on the application stack.", choices=("artisan", "composer", "yarn", "phpunit"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER, help="Optional arguments to pass to the specified tool.")

    parsed = parser.parse_args()

    if parsed.tool == "artisan":
        run(["docker-compose", "exec", "php", "php", "artisan"] + parsed.arguments)

    elif parsed.tool == "composer":
        run(["docker", "run", "--rm",
                              "--interactive",
                              "--tty",
                              "--user", f"{env['USER_ID']}:{env['GROUP_ID']}",
                              "--workdir", "/application",
                              "--mount", f"type=bind,source={os.getcwd()}/application/{env['PROJECT_NAME']},target=/application",
                              f"composer:{env['COMPOSER_IMAGE_TAG']}"] + parsed.arguments)

    elif parsed.tool == "yarn":
        run(["docker", "run", "--rm",
                              "--interactive",
                              "--tty",
                              "--user", f"{env['USER_ID']}:{env['GROUP_ID']}",
                              "--workdir", "/application",
                              "--mount", f"type=bind,source={os.getcwd()}/application/{env['PROJECT_NAME']},target=/application",
                              f"node:{env['NODE_IMAGE_TAG']}", "yarn"] + parsed.arguments)

    elif parsed.tool == "phpunit":
        run(["docker-compose", "exec", "php", "php", "./vendor/bin/phpunit"] + parsed.arguments)

    else:
        parser.print_help()
        sys.exit(1)
