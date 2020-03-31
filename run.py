#! /usr/bin/env python3

from scripting_utilities.print import Print
from laravel_docker.application import Application


if __name__ == "__main__":
    # try:
        application = Application()
        application.run()
    # except Exception as exception:
    #     Print.eol()
    #     Print.error(exception)
    #     Print.eol(2)
    # else:
    #     pass
    # finally:
    #     pass
