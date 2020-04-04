from laravel_docker.helpers import PrettyLog
from scripting_utilities.cd import ChangeDirectory
from scripting_utilities.skeleton import CreateSkeleton
from laravel_docker.core import Git, LaravelInstaller, ProjectConfiguration, ProjectEnvironment


class Application:
    """
    The main application - responsible for setting up the project.

    Attributes:
        _project_configuration (dictionary):
            The main environment/configuration array of the application.
    """


    def __init__(self):
        self._configuration = None


    @PrettyLog.start("Setting up a new Laravel project.")
    @PrettyLog.end("Your project was successfully installed.", type = "success")
    def run(self):
        """
        The main method. It is here that all the various steps
        - of setting up the project - are called.
        """

        self._configure()

        self._structure()
        self._scaffold()

        self._laravel()
        self._git()


    @PrettyLog.start("Configuring the project environment.")
    def _configure(self):
        """
        Ask the user some questions concerning the project to scaffold,
        and record the answers in the application's configuration dict.
        """

        self._configuration = ProjectEnvironment().initialize().get()


    @PrettyLog.start("Creating the project structure.")
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


    @PrettyLog.start("Scaffolding the project configuration files.")
    def _scaffold(self):
        """
        Create the project configuration files according to the templates.
        """

        ProjectConfiguration(self._configuration).setup()


    @PrettyLog.start("Pulling a fresh Laravel instance.")
    def _laravel(self):
        """
        Pull a fresh laravel application.
        """

        with ChangeDirectory(self._configuration["project"]["name"]):
            with ChangeDirectory("application"):
                LaravelInstaller(self._configuration).pull()


    @PrettyLog.start("Initializing a new git repository for the project.")
    def _git(self):
        """
        Initialize a git repo in the project root directory.
        """

        with ChangeDirectory(self._configuration["project"]["name"]):
            Git.initialize()
