import fileinput
import os
import re
import stat
from collections.abc import Mapping
from datetime import datetime, timedelta
from pathlib import Path
from subprocess import run

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from harivansh_scripting_utilities.helpers import cd

from harivansh_laravel_docker.helpers import Parser, Question, Validation


class ProjectEnvironment:
    """
    This class is responsible for asking the user questions about the project.

    Attributes:
        _configuration (dict):
            A mapping containing the project's environment configuration.
    """

    def __init__(self):
        self._configuration = {
            # Project-level configuration values.
            "project": {
                "name": None,
                "domain": "application.local",
            },

            # TLS/SSL configuration values.
            "ssl": {
                "key_name": "key.pem",
                "certificate_name": "certificate.pem"
            },

            # Docker-compose general environment values.
            "environment": {
                "uid": os.geteuid(),
                "gid": os.getegid()
            },

            # Docker-compose service environment values.
            "services": {
                "pgadmin": {
                    "email": "hello@harivan.sh",
                    "password": "password"
                },
                "selenium": {
                    "port": 4444
                }
            },

            # Application (laravel) specific values.
            "application": {
                # The values defined here will replace the corresponding ones defined in the .env file of the laravel
                # application.
                "environment": {
                    "APP_NAME": None,
                    "APP_URL": None,

                    "DB_CONNECTION": "pgsql",
                    "DB_HOST": "postgresql",
                    "DB_PORT": 5432,
                    "DB_DATABASE": "application",
                    "DB_USERNAME": "username",
                    "DB_PASSWORD": "password",

                    "CACHE_DRIVER": "redis",
                    "SESSION_DRIVER": "redis",
                    "QUEUE_CONNECTION": "redis",

                    "REDIS_HOST": "redis",
                    "REDIS_PORT": 6379
                }
            }
        }

    def initialize(self):
        """
        Initialize the configuration dictionary.
        This is done by asking the user a few questions concerning the configuration options of the project.

        Returns:
            self
        """

        self._configuration["project"]["name"] = self._query_project_name()
        self._configuration["project"]["domain"] = self._query_domain_name()

        self._configuration["application"]["environment"]["APP_NAME"] = self._configuration["project"]["name"]
        self._configuration["application"]["environment"][
            "APP_URL"] = f"https://{self._configuration['project']['domain']}"

        return self

    def get(self):
        """
        Get the current instance of the configuration dictionary.

        Returns:
            dict: The current configuration instance.
        """

        return self._configuration

    def _query_project_name(self):
        return str(Question(
            "Project name",
            (
                Validation.is_pascalcase,
                Validation.directory_exists
            )
        ))

    def _query_domain_name(self):
        return str(Question(
            "Project domain",
            (Validation.is_url,),
            self._configuration["project"]["domain"]
        ))


class CreateSkeleton:
    """
    A class to create a directory structure in the current directory depending on the structure defined.
    """

    def __init__(self, structure):
        """
        Class constructor.

        Args:
            structure (dict):
                The directory structure to create in the current directory.
                This is generally a dictionary of dictionaries or strings representing the directory structure.
                The empty dictionaries represent directories, while the empty strings represent files.

                e.g.: { "one": {
                            "eleven": {},
                            "twelve": {
                                "file.txt": "",
                                "anotherfile.jpeg": "",
                                "inner-directory": {}
                            }
                        },
                        "two.py": ""
                    }
        """

        CreateSkeleton._validate(structure)
        CreateSkeleton._create(structure)

    @staticmethod
    def _create(structure):
        """
        Create the provided files, and directories in the structure.

        Args:
            structure (Mapping): The directory structure to create in the current directory.
        """

        for name, structure in structure.items():
            if isinstance(structure, Mapping):
                os.mkdir(name)

                with cd(name):
                    CreateSkeleton._create(structure)
            elif structure == "":
                Path(name).touch()
            else:
                raise ValueError("The directory structure provided is ill-formed")

    @staticmethod
    def _validate(structure):
        """
        Validates the directory structure provided.

        Args:
            structure (Mapping): The directory structure to validate.

        Raises:
            ValueError: If the given structure is invalid.
        """

        error_message = "The directory structure provided is ill-formed"

        if not isinstance(structure, Mapping):
            raise ValueError(error_message)

        for name, structure in structure.items():
            if isinstance(structure, Mapping):
                CreateSkeleton._validate(structure)
            elif structure == "":
                pass
            else:
                raise ValueError(error_message)


class ProjectConfiguration:
    """
    This class is responsible for creating the appropriate project-level configuration files from the provided templates
    and provided environment variables.

    Attributes:
        _configuration (dict):
            The configuration / environment variables of the project.
    """

    def __init__(self, configuration):
        self._configuration = configuration

    def setup(self):
        """
        Set up the configuration files.
        """

        with cd(self._configuration["project"]["name"]):
            with cd("configuration"):
                with cd("nginx"):
                    with cd("conf.d"):
                        # default.conf
                        (Parser().read_template(Parser.template_path("configuration/nginx/default.conf"))
                         .parse({
                            "PROJECT_DOMAIN": self._configuration["project"]["domain"],
                            "SSL_KEY_NAME": self._configuration["ssl"]["key_name"],
                            "SSL_CERTIFICATE_NAME": self._configuration["ssl"]["certificate_name"]
                         })
                         .output("default.conf"))

                        # utils.conf
                        (Parser().read_template(Parser.template_path("configuration/nginx/utils.conf"))
                         .parse({
                            "PROJECT_DOMAIN": self._configuration["project"]["domain"]
                         })
                         .output("utils.conf"))

            with cd("dockerfiles"):
                with cd("php"):
                    # PHP Dockerfile
                    (Parser().read_template(Parser.template_path("dockerfiles/php/Dockerfile"))
                     .parse()
                     .output("Dockerfile"))

                    # entrypoint.sh
                    (Parser().read_template(Parser.template_path("dockerfiles/php/entrypoint.sh"))
                     .parse()
                     .output("entrypoint.sh"))

                    os.chmod("entrypoint.sh", os.stat("entrypoint.sh").st_mode | stat.S_IEXEC)

            # docker-compose.yml
            (Parser().read_template(Parser.template_path("docker-compose.yml"))
             .parse()
             .output("docker-compose.yml"))

            environment_variables = {
                "PROJECT_NAME": self._configuration["project"]["name"],
                "PROJECT_DOMAIN": self._configuration["project"]["domain"],
                "USER_ID": self._configuration["environment"]["uid"],
                "GROUP_ID": self._configuration["environment"]["gid"],
                "PGADMIN_EMAIL": self._configuration["services"]["pgadmin"]["email"],
                "PGADMIN_PASSWORD": self._configuration["services"]["pgadmin"]["password"],
                "SELENIUM_PORT": self._configuration["services"]["selenium"]["port"],
                "SSL_KEY_NAME": self._configuration["ssl"]["key_name"],
                "SSL_CERTIFICATE_NAME": self._configuration["ssl"]["certificate_name"],
                "DB_NAME": self._configuration["application"]["environment"]["DB_DATABASE"],
                "DB_USERNAME": self._configuration["application"]["environment"]["DB_USERNAME"],
                "DB_PASSWORD": self._configuration["application"]["environment"]["DB_PASSWORD"],
            }

            # .env (for docker-compose)
            (Parser().read_template(Parser.template_path("project.env"))
             .parse(environment_variables)
             .output(".env"))

            # .env.example
            (Parser().read_template(Parser.template_path("project.env"))
             .parse({name: "" for name in environment_variables})
             .output(".env.example"))

            # run.py
            (Parser().read_template(Parser.template_path("run.py"))
             .parse()
             .output("run"))

            os.chmod("run", os.stat("run").st_mode | stat.S_IEXEC)

            # .gitignore
            (Parser().read_template(Parser.template_path("project.gitignore"))
             .parse()
             .output(".gitignore"))

            # LICENSE
            (Parser().read_template(Parser.template_path("LICENSE"))
             .parse()
             .output("LICENSE"))

            # README.md
            (Parser().read_template(Parser.template_path("README.md"))
             .parse({
                "PROJECT_NAME": self._configuration["project"]["name"],
                "PROJECT_DOMAIN": self._configuration["project"]["domain"],
                "APP_URL": self._configuration["application"]["environment"]["APP_URL"],
                "SELENIUM_PORT": self._configuration["services"]["selenium"]["port"]
             })
             .output("README.md"))


class LaravelInstaller:
    """
    This class is responsible for pulling a fresh Laravel instance into the current project.

    Attributes:
        _configuration (dict):
            The configuration / environment variables of the project.
    """

    def __init__(self, configuration):
        self._configuration = configuration

    def pull(self):
        """
        Pull a fresh Laravel application.
        """

        run([
            "docker", "run",
            "--rm",
            "--interactive",
            "--tty",
            "--user", f"{self._configuration['environment']['uid']}:{self._configuration['environment']['gid']}",
            "--mount", f"type=bind,source={os.getcwd()},target=/application",
            "--workdir", "/application",
            "composer", "create-project",
            "--prefer-dist",
            "--ignore-platform-reqs",
            "laravel/laravel", self._configuration["project"]["name"]
        ],
            check=True
        )


class Env:
    """
    This class is responsible for the changes made to the application's (laravel) .env file.

    Attributes:
        _env_path (str):
            The path to the application's (laravel) .env file.
    """

    def __init__(self, env_path):
        """
        Class constructor.

        Args:
            env_path (str):
                The file path to the application's (laravel) .env file.
        """

        self._env_path = env_path

    def replace(self, replacement):
        """
        Replace the environment values with the ones provided.

        Args:
            replacement (dict):
                The values to replace the current environment with.
        """

        if not isinstance(replacement, Mapping):
            raise ValueError("The replacement argument should be a Mapping.")

        with fileinput.input(self._env_path, inplace=True) as env:
            env_regex = re.compile(r"^(?P<key>\w+)=(?P<value>[\S]+)?\s*(?P<remaining>#.*)?$")

            for line in env:
                line = line.strip()
                matches = env_regex.match(line)

                if matches is not None:
                    matches = matches.groupdict()
                    line = f"{matches['key']}={replacement[matches['key']] if matches['key'] in replacement else matches['value']}"

                    if matches['remaining']:
                        line = f"{line}{' ' * 4}{matches['remaining']}"

                print(line)


class Ssl:
    """
    This class is responsible for creating a x509 TLS/SSL certificate and the associated key.

    Attributes:
        _hostname (str):
            The hostname of the machine on which the certificates will be hosted.

        _key_size (int):
            The size of the SSL key.

        _validity (int):
            The number number of days (since creation) for which the certificate
            will remain valid.

        _key (bytes):
            The TLS key content.

        _certificate (bytes):
            The TLS certificate content.
    """

    def __init__(self, hostname, key_size=4096, validity=365):
        self._hostname = hostname
        self._key_size = key_size
        self._validity = validity
        self._key = None
        self._certificate = None

    def generate(self):
        """
        Generate the TLS/SSL key and certificate.

        Return:
            self
        """

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self._key_size,
            backend=default_backend(),
        )

        name = x509.Name([
            x509.NameAttribute(x509.NameOID.COMMON_NAME, self._hostname)
        ])

        san = x509.SubjectAlternativeName([
            x509.DNSName(self._hostname)
        ])

        basic_constraints = x509.BasicConstraints(ca=True, path_length=0)
        now = datetime.utcnow()

        cert = (
            x509.CertificateBuilder()
                .subject_name(name)
                .issuer_name(name)
                .public_key(key.public_key())
                .serial_number(1000)
                .not_valid_before(now)
                .not_valid_after(now + timedelta(days=self._validity))
                .add_extension(basic_constraints, False)
                .add_extension(san, False)
                .sign(key, hashes.SHA256(), default_backend())
        )

        self._certificate = cert.public_bytes(encoding=serialization.Encoding.PEM)
        self._key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        return self

    def write(self, key_path="key.pem", certificate_path="certificate.pem"):
        """
        Write the generated certificates to a binary file.

        Args:
            key_path (str): The path where the key will be stored.
            certificate_path (str): The path where the certificate will be stored.
        """

        with open(key_path, "wb") as key:
            key.write(self._key)

        with open(certificate_path, "wb") as certificate:
            certificate.write(self._certificate)
