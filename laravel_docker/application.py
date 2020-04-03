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


    @property
    def project_configuration(self):
        return self._project_configuration


    def run(self):
        self._initialize_project_configuration()
        self._setup_project_structure()
        self._add_configuration_files()


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
                "application": {
                    ".gitkeep": ""
                }
            }
        })


    def _add_configuration_files(self):
        with ChangeDirectory(self.project_configuration["project"]["name"]):
            with ChangeDirectory("configuration"):
                # nginx.conf
                with ChangeDirectory("nginx"):
                    (Parser().read_template(Parser.template_path("configuration/nginx/nginx.conf"))
                             .parse({
                                 "PROJECT_DOMAIN": self.project_configuration["project"]["domain"]
                             })
                             .output("nginx.conf"))

                with ChangeDirectory("php"):
                    # crontab
                    (Parser().read_template(Parser.template_path("configuration/php/crontab"))
                             .parse()
                             .output("crontab"))

                    # supervisord.conf
                    #@TODO: REVIEW THE SUPERVISORD DOCS
                    with ChangeDirectory("supervisor"):
                        (Parser().read_template(Parser.template_path("configuration/php/supervisor/supervisord.conf"))
                                 .parse()
                                 .output("supervisord.conf"))

            with ChangeDirectory("dockerfiles"):
                # PHP Dockerfile
                with ChangeDirectory("php"):
                    (Parser().read_template(Parser.template_path("dockerfiles/php/Dockerfile"))
                             .parse()
                             .output("Dockerfile"))

            # docker-compose.yml
            (Parser().read_template(Parser.template_path("docker-composer.yml"))
                     .parse()
                     .output("docker-composer.yml"))

            # .env (for docker-compose)
            (Parser().read_template(Parser.template_path("project.env"))
                     .parse({
                         "PROJECT_NAME": self.project_configuration["project"]["name"],
                         "USER_ID": self.project_configuration["environment"]["uid"],
                         "GROUP_ID": self.project_configuration["environment"]["gid"]
                     })
                     .output(".env"))

            # .env.example
            (Parser().read_template(Parser.template_path("project.env"))
                     .parse({
                         "PROJECT_NAME": "",
                         "USER_ID": "",
                         "GROUP_ID": ""
                     })
                     .output(".env.example"))

            # run.py
            #@TODO: MAKE THE RUN BINARY EXECUTABLE
            (Parser().read_template(Parser.template_path("run.py"))
                     .parse()
                     .output("run.py"))

            # .gitignore
            (Parser().read_template(Parser.template_path("project.gitignore"))
                     .parse()
                     .output(".gitignore"))
