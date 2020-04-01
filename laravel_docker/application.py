from laravel_docker.getters import Options
from scripting_utilities.print import Print


class Application:


    def __init__(self):
        Print.eol()
        Print.info("Setting up a new Laravel project.")
        Print.eol(2)

        self.options = None


    def run(self):
        options = Options()
        self.options = options.get()
