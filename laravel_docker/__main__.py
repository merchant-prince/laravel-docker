from scripting_utilities import Print
from laravel_docker import Application


if __name__ == "__main__":
    try:
        Application().run()
    except Exception as exception:
        Print.eol()
        Print.error(exception)
        Print.eol(2)
