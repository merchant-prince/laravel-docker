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

This package is used to automate the installation of a [Laravel](https://laravel.com) project with the associated
surrounding system (database, redis, adminer, etc...) on [Docker](https://www.docker.com).

## Installation

This project can be installed using [pip](https://pip.pypa.io/en/stable).
The relevant package can be found [here](https://pypi.org/project/harivansh-laravel-docker).
The installation can be done as follows:

```sh
pip install harivansh-laravel-docker
```

This will install the package, and any associated dependencies required to run it.

### Requirements

The package author assumes the following:

* This package is run in a UNIX terminal (xterm-256color compatible)
* The environment has [Docker](https://www.docker.com) installed

## Usage

To run the application and install a new Laravel project in the current working directory, run the following command:

```sh
python3 -m harivansh_laravel_docker
```

## Testing

To run the tests, ```cd``` into the root project directory, and run the following:

```sh
./dev.py test
```

## Building

To build the **whl** and **tar** packages, ```cd``` into the root project directory, and run the following:

```sh
./dev.py build
```

## Pushing

To push the build package to pypi, first make sure the **.credentials** file is populated with your username, and
password. Then run the following command:

```sh
./dev.py build --push
```
