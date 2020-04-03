#! /usr/bin/env python3


import os
import sys
import argparse
from subprocess import run


if __name__ == "__main__":
    #@TODO: THIS FILE NEEDS TO DEPEND ON THE .env FILE FOR VARIABLES
    parser = argparse.ArgumentParser(description="Perform common tasks on the [[PROJECT_NAME]] application stack.")

    parser.add_argument("tool", help="Define a tool to use on the application stack.", choices=("artisan", "composer", "yarn", "phpunit"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER, help="Optional arguments to pass to the specified tool.")

    parsed = parser.parse_args()

    if parsed.tool == "artisan":
        run(["docker-compose", "exec", "php", "php", "artisan"] + parsed.arguments)

    elif parsed.tool == "composer":
        run(["docker-compose", "exec", "php", "composer"] + parsed.arguments)

    elif parsed.tool == "yarn":
        run(["docker", "run", "--rm",
                              "--interactive",
                              "--tty",
                              "--user", f"{os.geteuid()}:{os.getegid()}",
                              "--workdir", "/application",
                              "--mount", f"type=bind,source={os.getcwd()}/application/[[PROJECT_NAME]],target=/application",
                              "node", "yarn"] + parsed.arguments)

    elif parsed.tool == "phpunit":
        run(["docker-compose", "exec", "php", "php", "./vendor/bin/phpunit"] + parsed.arguments)

    else:
        parser.print_help()
        sys.exit(1)
