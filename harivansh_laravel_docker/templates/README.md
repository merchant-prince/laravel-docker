# [[PROJECT_NAME]]

## Architecture

The directory structure of this project is as follows:

```
[[PROJECT_NAME]]      <----  The root project directory
│
├── application
│   └── [[PROJECT_NAME]]      <----  The Laravel application
│
├── configuration
│   ├── nginx
│   │   ├── conf.d
│   │   │   ├── default.conf    <----  The application's nginx.conf file
│   │   │   └── utils.conf      <----  The other tools' (adminer, etc...) nginx.conf file
│   │   │
│   │   └── ssl                 <----  The TLS/SSL certificate and key
│   │       ├── certificate.pem
│   │       └── key.pem
│   └── php
│       └── custom-php.ini      <----  A php.ini file to override the default values
│
├── docker-compose.yml
│
├── dockerfiles
│   │
│   └── php
│       ├── Dockerfile      <----  Custom dockerfile for the php service
│       └── entrypoint.sh   <----  Custom entrypoint for the php service
│
├── .env        <----  The main configuration/environment file of the project
│
├── .env.example
│
├── .gitignore
│
├── LICENSE
│
├── README.md
│
└── run     <----  An executable script used to run several commands on the
                    Laravel application
```

## Configuration

The main configuration of the project lies in the ```.env``` file.
It consists of several environment/configuration variables which are used during
the build step of the docker containers, and when running the application.

It is a **dumb** version of a typical dotenv file. It **only** supports the
following template for each line:

```env
ENVIRONMENT_VARIABLE_NAME=VALUE

...
```

Each line in the file should adhere to the following regex:

```regex
^([a-zA-Z][a-zA-Z0-9_]*)=(.*)?$
```

The only two files that require this file to run are:

* docker-compose.yml
* run

## Running

To start the Laravel application, ```cd``` in the project root directory and run
the following:

```sh
docker-compose up
```

This will start the project, and the laravel application will be accessible
at the domain defined during the installation.
This defaults to [https://application.local](https://application.local).

## Commands

The ```run``` executable is a convenience script used to run commonly used
commands in the Laravel application.

It supports the following commands:

```sh
# ARTISAN
# To run any artisan command
# The php service needs to be running for the following command to work

./run artisan COMMAND [ARGS]

# e.g.: ./run artisan migrate:fresh --seed


# COMPOSER
# To run any composer command in the php service
# The php service needs to be running for the following command to work

./run composer COMMAND [ARGS]

# e.g.: ./run composer require carbon/carbon


# YARN
# To run any yarn command for the laravel project

./run yarn COMMAND [ARGS]

# e.g.: ./run yarn watch-poll


# PHPUNIT
# To run any tests defined in the /tests directory of the Laravel project
# The php service needs to be running for the following command to work

./run phpunit [COMMAND [ARGS]]

# e.g.: ./run phpunit
```

## Optional Packages

### [Dusk](https://laravel.com/docs/master/dusk)

The **selenium**, and **firefox** services are available by default to be used with dusk. If you are not using the
laravel/dusk framework for testing, remove the aforementioned services from the project's **docker-compose.yml** file.

If you are using laravel/dusk for testing, then, after requiring & installing laravel/dusk, you need to setup the
**tests/DuskTestCase.php** file to resemble the following snippet:

```php
// [DuskTestCase.php]

...

public static function prepare()
{
    // static::startChromeDriver();
}

...

protected function driver()
{
    return RemoteWebDriver::create(
        'http://selenium:4444/wd/hub',
        DesiredCapabilities::firefox()
            ->setCapability("acceptInsecureCerts", true)
    );
}

...
```

## FAQ

Visit [makeareadme](https://www.makeareadme.com) for a detailed explanation on
creating readmes.
