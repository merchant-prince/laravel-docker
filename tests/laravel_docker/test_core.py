import os
from unittest import TestCase

from harivansh_scripting_utilities.helpers import cd, capturestdout, injectstdin, tmpdir

from laravel_docker.core import CreateSkeleton, Env, ProjectEnvironment, Ssl


class TestProjectEnvironment(TestCase):

    def test_environment_uid_and_gid_are_correctly_set(self):
        project_environment = ProjectEnvironment()

        self.assertEqual(project_environment.get()["environment"]["uid"], os.geteuid())
        self.assertEqual(project_environment.get()["environment"]["gid"], os.getegid())

    def test_a_non_pascal_cased_project_name_is_rejected(self):
        project_environment = ProjectEnvironment()
        project_name = "project-one"
        max_tries = 3

        with capturestdout(), injectstdin(f"{project_name}\n" * max_tries):
            self.assertRaises(ValueError, project_environment._query_project_name)

    def test_project_name_is_rejected_if_cwd_has_a_directory_with_the_same_name(self):
        project_name = "TheAwesomeProjectWithAnAwesomeName"

        with tmpdir():
            os.mkdir(project_name)

            project_environment = ProjectEnvironment()
            max_tries = 3

            with capturestdout(), injectstdin(f"{project_name}\n" * max_tries):
                self.assertRaises(ValueError, project_environment._query_project_name)

    def test_a_pascal_cased_non_existent_project_name_is_accepted(self):
        project_environment = ProjectEnvironment()
        project_name = "CorrectProjectName"

        with capturestdout(), injectstdin(project_name):
            captured_project_name = project_environment._query_project_name()

        self.assertEqual(captured_project_name, project_name)

    def test_an_invalid_domain_is_not_accepted(self):
        project_environment = ProjectEnvironment()
        invalid_domain = "invalid domain.com"
        max_tries = 3

        with capturestdout(), injectstdin(f"{invalid_domain}\n" * max_tries):
            self.assertRaises(ValueError, project_environment._query_domain_name)

    def test_a_valid_domain_name_is_accepted(self):
        project_environment = ProjectEnvironment()
        domain = "application.local"

        with capturestdout(), injectstdin(domain):
            captured_domain = project_environment._query_domain_name()

        self.assertEqual(captured_domain, domain)

    def test_a_null_value_defaults_to_the_provided_domain(self):
        project_environment = ProjectEnvironment()
        domain = "admin.application.local"
        project_environment._configuration["project"]["domain"] = domain

        with capturestdout(), injectstdin("\n"):
            captured_domain = project_environment._query_domain_name()

        self.assertEqual(captured_domain, domain)


class TestCreateSkeleton(TestCase):

    def test_does_not_raise_exception_on_valid_structure_validation(self):
        valid_structure = {
            "directory_1": {},
            "file_1": "",
            "directory_2": {
                "inner_file_1": "",
                "inner_directory_1": {},
                "inner_file_2": ""
            },
            "file_2": ""
        }

        CreateSkeleton._validate(valid_structure)

    def test_raises_exceptions_on_invalid_structure_validation(self):
        invalid_structure = {
            "directory_1": {},
            "file_1": "",
            "directory_2": {
                "inner_file_1": "",
                "inner_directory_1": [],
                "inner_file_2": ""
            },
            "file_2": ()
        }

        self.assertRaises(ValueError, CreateSkeleton._validate, invalid_structure)

    def test_creates_skeleton_if_a_valid_structure_is_provided(self):
        valid_structure = {
            "directory_1": {},
            "file_1": "",
            "directory_2": {
                "inner_file_1": "",
                "inner_directory_1": {},
                "inner_file_2": ""
            },
            "file_2": ""
        }

        with tmpdir():
            CreateSkeleton(valid_structure)

            self.assertTrue(os.path.isdir("directory_1"))
            self.assertTrue(os.path.isfile("file_1"))
            self.assertTrue(os.path.isdir("directory_2"))

            with cd("directory_2"):
                self.assertTrue(os.path.isfile("inner_file_1"))
                self.assertTrue(os.path.isdir("inner_directory_1"))
                self.assertTrue(os.path.isfile("inner_file_2"))

            self.assertTrue(os.path.isfile("file_2"))

    def test_throws_an_exception_and_does_not_create_any_files_when_invalid_structure_provided(self):
        invalid_structure = {
            "directory_1": [],
            "file_1": "",
            "directory_2": {
                "inner_file_1": 12,
                "inner_directory_1": {},
                "inner_file_2": ()
            },
            "file_2": ""
        }

        with tmpdir():
            self.assertRaises(ValueError, CreateSkeleton, invalid_structure)
            self.assertFalse(os.listdir())


class TestEnv(TestCase):

    def test_an_exception_is_thrown_if_the_replacement_argument_is_not_a_mapping(self):
        env_path = ".env"
        replacement = ["one", "two"]

        env = Env(env_path)

        self.assertRaises(ValueError, env.replace, replacement)

    def test_a_correctly_formatted_env_file_is_successfully_processed(self):
        with tmpdir():
            env_filename = ".env"
            env_file_content = """
                APP_NAME="OneTwo"
                APP_URL="http://application.local"

                DB_USERNAME=username # This is a partial line comment also with an = character.
                DB_PASSWORD=password # is this le password?

                # This is a full line comment with an = character.
                DB_PORT=5432
            """

            with open(env_filename, "w") as env:
                env.write(env_file_content)

            replacement = {
                "APP_NAME": "FiveSix",
                "APP_URL": "https://nope.dev",

                "DB_USERNAME": "le_username"
            }

            Env(env_filename).replace(replacement)

            expected_env_file_content = f"""
APP_NAME={replacement['APP_NAME']}
APP_URL={replacement['APP_URL']}

DB_USERNAME={replacement['DB_USERNAME']}    # This is a partial line comment also with an = character.
DB_PASSWORD=password    # is this le password?

# This is a full line comment with an = character.
DB_PORT=5432
"""

            with open(env_filename) as env:
                actual_env_file_content = env.read()

                # The actual .env file has an additional newline character.
                # We need to remove it so that the following assertion passes.
                self.assertEqual(expected_env_file_content, actual_env_file_content[:-1])


class TestSsl(TestCase):

    def test_ssl_certificates_are_successfully_written_to_the_specified_paths(self):
        key_directory = "ssl-key"
        key_filename = "le-key"

        certificate_directory = "ssl-certificate"
        certificate_filename = "le-certificate"

        with tmpdir():
            os.mkdir(key_directory)
            os.mkdir(certificate_directory)

            key_path = f"{key_directory}/{key_filename}"
            certificate_path = f"{certificate_directory}/{certificate_filename}"

            ssl = Ssl("application.local").generate()

            self.assertTrue(bool(ssl._key))
            self.assertTrue(bool(ssl._certificate))

            ssl.write(key_path, certificate_path)

            self.assertTrue(
                os.path.isfile(key_path) and os.path.isfile(certificate_path)
            )
