#! /usr/bin/env python3


"""
This script is used to initialize and run the main application.
"""


# from scripting_utilities.print import Print
from laravel_docker.application import Application


if __name__ == "__main__":
    # try:
    Application().run()
    # except Exception as exception:
    #     Print.eol()
    #     Print.error(exception)
    #     Print.eol(2)
    # else:
    #     pass
    # finally:
    #     pass
