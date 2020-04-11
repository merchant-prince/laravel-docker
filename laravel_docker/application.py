from subprocess import run

from harivansh_scripting_utilities.helpers import cd

from laravel_docker.core import CreateSkeleton, Env, LaravelInstaller, ProjectConfiguration, ProjectEnvironment, Ssl
from laravel_docker.helpers import log


class Application:
    """
    The main application - responsible for setting up the project.

    Attributes:
        _configuration (dict):
            The main environment/configuration array of the application.
    """

    def __init__(self):
        self._configuration = None

    @log("Setting up a new Laravel project.")
    @log("Your project was successfully installed.", type="success", position="after")
    def run(self):
        """
        The main method. It is here that all the various steps - of setting up the project - are called.
        """

        (self
         ._pre_install()
         ._install()
         ._post_install())

    def _pre_install(self):
        self._configure()

        return self

    def _install(self):
        self._structure()
        self._ssl()
        self._scaffold()
        self._laravel()

        return self

    def _post_install(self):
        self._git()
        self._env()

        return self

    @log("Configuring the project environment.")
    def _configure(self):
        """
        Ask the user some questions concerning the project to scaffold, and record the answers in the configuration
        dict.
        """

        self._configuration = ProjectEnvironment().initialize().get()

    @log("Creating the project structure.")
    def _structure(self):
        """
        Create the project structure.
        """

        CreateSkeleton({
            self._configuration["project"]["name"]: {
                "configuration": {
                    "nginx": {
                        "conf.d": {},
                        "ssl": {}
                    },
                    "php": {
                        "custom-php.ini": ""
                    },
                },
                "dockerfiles": {
                    "php": {}
                },
                "application": {}
            }
        })

    @log("Generating SSL certificates.")
    def _ssl(self):
        """
        Generate TLS / SSL certificates.
        """

        with cd(self._configuration["project"]["name"]):
            with cd("configuration"):
                with cd("nginx"):
                    with cd("ssl"):
                        key_path = f"{self._configuration['ssl']['key_name']}"
                        certificate_path = f"{self._configuration['ssl']['certificate_name']}"

                        (Ssl(self._configuration["project"]["domain"])
                         .generate()
                         .write(key_path, certificate_path))

    @log("Scaffolding the project configuration files.")
    def _scaffold(self):
        """
        Create the project configuration files according to the templates.
        """

        ProjectConfiguration(self._configuration).setup()

    @log("Pulling a fresh Laravel instance.")
    def _laravel(self):
        """
        Pull a fresh laravel application.
        """

        with cd(self._configuration["project"]["name"]):
            with cd("application"):
                LaravelInstaller(self._configuration).pull()

    @log("Initializing a new git repository for the project.")
    def _git(self):
        """
        Initialize a git repository in the project root directory.
        """

        git_commands = [
            ["git", "init"],
            ["git", "add", "."],
            ["git", "commit", "-m", "initial commit"],
            ["git", "checkout", "-b", "development"]
        ]

        with cd(self._configuration["project"]["name"]):
            for git_command in git_commands:
                run(git_command, check=True)

    @log("Editing the application's environment file.")
    def _env(self):
        """
        Change the environment variables of the laravel application.
        """

        project_name = self._configuration["project"]["name"]
        environment_variables = self._configuration["application"]["environment"]

        with cd(project_name):
            with cd("application"):
                with cd(project_name):
                    Env(".env").replace(environment_variables)
