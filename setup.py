from setuptools import find_packages, setup


with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name = "harivansh-laravel-docker",
    version = "0.1.1-rc.2",
    description = "A package to automate the installation of Laravel projects on Docker.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/merchant-prince/laravel-docker",
    author = "Harivansh",
    author_email = "hello@harivan.sh",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX"
    ],
    keywords = "laravel docker",
    packages = find_packages(),
    package_data = {"templates": ["templates/*"]},
    python_requires = '>=3.8',
    install_requires = [
        "cryptography",
        "harivansh-scripting-utilities"
    ]
)
