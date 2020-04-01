from scripting_utilities.print import Print
from laravel_docker.getters import Configuration


class Application:


    def __init__(self):
        Print.eol()
        Print.info("Setting up a new Laravel project.")
        Print.eol(2)

        self.configuration = None


    def run(self):
        configuration = Configuration()

        configuration.initialize()

        self.configuration = configuration.get()
