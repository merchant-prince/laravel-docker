from scripting_utilities.print import Print
from laravel_docker.core import ProjectConfiguration
from scripting_utilities.skeleton import CreateSkeleton


class Application:


    def __init__(self):
        Print.eol()
        Print.info("Setting up a new Laravel project.")
        Print.eol(2)

        self._project_configuration = None


    def run(self):
        self._initialize_project_configuration()


    @property
    def project_configuration(self):
        return self._project_configuration


    def _initialize_project_configuration(self):
        project_configuration = ProjectConfiguration()

        project_configuration.initialize()

        self._project_configuration = project_configuration.get()


    def _setup_project_structure(self):
        CreateSkeleton({
            self.project_configuration["project"]["name"]: {
                "configuration": {
                    "nginx": {
                        "configuration": {}
                    },
                    "php": {
                        "configuration": {},
                        "supervisor": {}
                    },
                },
                "dockerfiles": {
                    "php": {}
                },
                "application": {}
            }
        })
