import os
from scripting_utilities.print import Print
from scripting_utilities.cd import ChangeDirectory
from scripting_utilities.skeleton import CreateSkeleton
from laravel_docker.core import ProjectConfiguration, Parser


class Application:


    def __init__(self):
        Print.eol()
        Print.info("Setting up a new Laravel project.")
        Print.eol(2)

        self._project_configuration = None
        self._template_path = os.path.dirname(os.path.abspath(__file__))


    @property
    def project_configuration(self):
        return self._project_configuration


    def run(self):
        self._initialize_project_configuration()
        self._setup_project_structure()


    def template_path(path = ""):
        return self._template_path + path


    def _initialize_project_configuration(self):
        project_configuration = ProjectConfiguration()

        project_configuration.initialize()

        self._project_configuration = project_configuration.get()


    def _setup_project_structure(self):
        CreateSkeleton({
            self.project_configuration["project"]["name"]: {
                "configuration": {
                    "nginx": {},
                    "php": {
                        "supervisor": {}
                    },
                },
                "dockerfiles": {
                    "php": {}
                },
                "application": {}
            }
        })


    def _add_project_structure_files(self):
        with ChangeDirectory(self.project_configuration["project"]["name"]):
            pass
