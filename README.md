# Laravel Docker

![Project status](https://img.shields.io/badge/status-active-brightgreen?&style=flat-square)
&nbsp;&nbsp;&nbsp;&nbsp;
![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/merchant-prince/laravel-docker?label=version&style=flat-square)
&nbsp;&nbsp;&nbsp;&nbsp;
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/harivansh-laravel-docker?style=flat-square)
&nbsp;&nbsp;&nbsp;&nbsp;
![PyPI - Wheel](https://img.shields.io/pypi/wheel/harivansh-laravel-docker?style=flat-square)
&nbsp;&nbsp;&nbsp;&nbsp;
![GitHub](https://img.shields.io/github/license/merchant-prince/laravel-docker?style=flat-square)

This package is used to automate the installation of a
[Laravel](https://laravel.com) project with the associated surrounding system
(database, redis, adminer, etc...) on [Docker](https://www.docker.com).

## Installation

This project can be installed using [pip](https://pip.pypa.io/en/stable).
The relevant package can be found
[here](https://pypi.org/project/harivansh-laravel-docker).
The installation can be done as follows:

```sh
pip install harivansh-laravel-docker
```

This will install the package, and any associated dependencies required to run
it.

### Requirements

The package author assumes the following:

* This package is run in a UNIX terminal (xterm-256color)
* The environment must have [Docker](https://www.docker.com) installed

## Usage

To run the application and install a new Laravel project in the current working
directory, run the following command:

```sh
python3 -m laravel_docker
```

## Testing

To run the tests, ```cd``` into the root project directory, and run the
following:

```sh
python -m unittest discover
```

## Testing Builds

Before pushing, we need to check whether the package is correctly formatted for
pypi.

```sh
# setup venv
python3 -m venv .env/build-test

# activate venv
source ./.env/build-test/bin/activate

# upgrade pip
pip install --upgrade pip

# install the package
pip install -e .

# go in the python interpreter to check if the module is available
python3

>>> from laravel_docker import Application
>>> Application().run()

...

```

## Building

To build a **tar** and **whl** version of the package, ```cd``` into the
root project directory, and run the following:

```sh
# setup venv
python3 -m venv .env/dev

# activate venv
source ./.env/dev/bin/activate

# upgrade pip
pip install --upgrade pip

# install the necessary packages
python3 -m pip install --upgrade setuptools twine wheel

# remove the dist files if present
rm -rf build dist harivansh_scripting_utilities.egg-info

# generate the dist files
python3 setup.py sdist bdist_wheel

# upload to pypi
python3 -m twine upload dist/*

#   username: __token__
#   password: pypi-api-token
```
