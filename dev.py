#! /usr/bin/env python3

import os
import re
import sys
import shutil
import argparse
from subprocess import run


def env(filepath):
    key_value_regex = re.compile(r"^(?P<key>\w+)=(?P<value>.*)$")
    result = {}

    with open(filepath) as dotfile:
        for line in dotfile:
            line = line.strip()
            matches = key_value_regex.match(line).groupdict()
            result[matches["key"]] = matches["value"]

    return result


def build_image(name, tag, target):
    run(["docker", "build",
         "--file", "dev.Dockerfile",
         "--build-arg", f"USER={os.geteuid()}",
         "--build-arg", f"GROUP={os.getegid()}",
         "--target", target,
         "--tag", f"{name}:{tag}",
         "."],
        check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test or build (and optionally push) the current python project.")
    parser.add_argument("action", choices=("build", "test"), help="Define an action to take.")
    parser.add_argument("--push", action="store_true", default=False, help="Whether to push the project to pypi.")
    arguments = parser.parse_args()

    image_name = "harivansh_laravel_docker_image"

    if arguments.action == "test":
        image_tag = "test"
        build_image(image_name, image_tag, target="test")

        run(["docker", "run",
             "--rm",
             "--user", f"{os.geteuid()}:{os.getegid()}",
             f"{image_name}:{image_tag}",
             "python3", "-m", "unittest", "discover", "-s", "tests/harivansh_laravel_docker"],
            check=True)

    elif arguments.action == "build":
        image_tag = "build"
        build_image(image_name, image_tag, target="build")

        dist_dirname = "dist"

        if os.path.isdir(dist_dirname):
            shutil.rmtree(dist_dirname)

        os.mkdir(dist_dirname)

        run(["docker", "run",
             "--rm",
             "--user", f"{os.getuid()}:{os.getegid()}",
             "--mount", f"type=bind,source={os.getcwd()}/{dist_dirname},dst=/application/{dist_dirname}",
             f"{image_name}:{image_tag}",
             "python3", "setup.py", "sdist", "bdist_wheel"],
            check=True)

        if arguments.push:
            credentials = env(".credentials")

            run(["docker", "run",
                 "--rm",
                 "--user", f"{os.geteuid()}:{os.getegid()}",
                 "--mount", f"type=bind,source={os.getcwd()}/{dist_dirname},dst=/application/{dist_dirname},readonly",
                 f"{image_name}:{image_tag}",
                 "twine", "upload",
                 "--username", credentials["USERNAME"],
                 "--password", credentials["PASSWORD"],
                 "dist/*"],
                check=True)

    else:
        parser.print_help()
        sys.exit(1)
