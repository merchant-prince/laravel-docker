import setuptools


with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name = "harivansh-laravel-docker",
    version = "0.1.0",
    author = "Harivansh",
    author_email = "hello@harivan.sh",
    description = "A package to automate the installation of Laravel projects.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/merchant-prince/laravel-docker",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT",
        "Operating System :: POSIX"
    ],
    python_requires = '>=3.8',
)
