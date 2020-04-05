from laravel_docker.helpers import PrettyLog
from scripting_utilities import ChangeDirectory, CreateSkeleton
from laravel_docker.core import Env, Git, LaravelInstaller, ProjectConfiguration, ProjectEnvironment


class Application:
    """
    The main application - responsible for setting up the project.

    Attributes:
        _project_configuration (dictionary):
            The main environment/configuration array of the application.
    """


    def __init__(self):
        self._configuration = None


    @PrettyLog.message("Setting up a new Laravel project.")
    @PrettyLog.message("Your project was successfully installed.", position = "after", type = "success")
    def run(self):
        """
        The main method. It is here that all the various steps
        - of setting up the project - are called.
        """

        (self._pre_install()
             ._install()
             ._post_install())


    def _pre_install(self):
        self._configure()

        return self


    def _install(self):
        self._structure()
        self._scaffold()
        self._laravel()

        return self


    def _post_install(self):
        self._git()
        self._env()

        return self


    @PrettyLog.message("Configuring the project environment.")
    def _configure(self):
        """
        Ask the user some questions concerning the project to scaffold,
        and record the answers in the application's configuration dict.
        """

        self._configuration = ProjectEnvironment().initialize().get()


    @PrettyLog.message("Creating the project structure.")
    def _structure(self):
        """
        Create the project structure.
        """

        CreateSkeleton({
            self._configuration["project"]["name"]: {
                "configuration": {
                    "nginx": {}
                },
                "dockerfiles": {
                    "php": {}
                },
                "application": {}
            }
        })


    @PrettyLog.message("Scaffolding the project configuration files.")
    def _scaffold(self):
        """
        Create the project configuration files according to the templates.
        """

        ProjectConfiguration(self._configuration).setup()


    @PrettyLog.message("Pulling a fresh Laravel instance.")
    def _laravel(self):
        """
        Pull a fresh laravel application.
        """

        with ChangeDirectory(self._configuration["project"]["name"]):
            with ChangeDirectory("application"):
                LaravelInstaller(self._configuration).pull()


    @PrettyLog.message("Initializing a new git repository for the project.")
    def _git(self):
        """
        Initialize a git repository in the project root directory.
        """

        with ChangeDirectory(self._configuration["project"]["name"]):
            Git.initialize()


    def _env(self):
        """
        Change the environment variables of the laravel application.
        """

        project_name = self._configuration["project"]["name"]
        environment_variables = self._configuration["application"]["environment"]

        with ChangeDirectory(project_name):
            with ChangeDirectory("application"):
                with ChangeDirectory(project_name):
                    Env(".env").replace(environment_variables)
