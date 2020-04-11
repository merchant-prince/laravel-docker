from harivansh_scripting_utilities.print import error

from laravel_docker.application import Application

if __name__ == "__main__":
    try:
        Application().run()
    except Exception as exception:
        print(error(f"\n{exception}\n\n"), end="")
