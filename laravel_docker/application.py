from scripting_utilities.print import Print
from laravel_docker.core.options import Options


class Application:


    def __init__(self):
        Print.eol()
        Print.info("Setting up a new Laravel project.")
        Print.eol(2)

        self.options = None


    def run(self):
        options = Options()
        self.options = options.get()
