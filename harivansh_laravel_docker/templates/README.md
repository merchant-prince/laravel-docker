# [[PROJECT_NAME]]

## Architecture

Its directory structure of is as follows:

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
└── run     <----  An executable script used to run several commands on the Laravel application
```

## Configuration

The main configuration of the project lies in the ```.env``` file.
It consists of several environment/configuration variables which are used during the build step of the docker
containers, and when running the application.

It is a **dumb** version of a typical dotenv file. It **only** supports the following template for each line:

```env
ENVIRONMENT_VARIABLE_NAME=VALUE

...
```

Each line in the file should adhere to the following regex:

```regex
^([a-zA-Z][a-zA-Z0-9_]*)=(.*)?$
```

The files that require this file to run are:

* docker-compose.yml
* run

## Running

To start the Laravel application, ```cd``` in the project root directory and run the following:

```sh
docker-compose up
```

This will start the project, and the laravel application will be available at [[[APP_URL]]]([[APP_URL]]).

## Services

The following services are available in this stack:

<dl>
    <dt>Nginx</dt>
    <dd>This service exposes ports 80 and 443 from which the Laravel application, and PgAdmin will be accessible.</dd>
    <dt>PHP</dt>
    <dd>The php fpm server for nginx. It handles all the calls to PHP.</dd>
    <dt>PostgreSQL</dt>
    <dd>The application's main database.</dd>
    <dt>Redis</dt>
    <dd>The redis server used in several contexts across the Laravel application.</dd>
    <dt>PgAdmin</dt>
    <dd>This service exposes the PgAdmin application at http://pgadmin.[[PROJECT_DOMAIN]].</dd>
    <dt>Selenium</dt>
    <dd>This is the selenium hub used for testing the Laravel application through dusk.</dd>
    <dt>Firefox</dt>
    <dd>This is the browser used for testing the application through dusk.</dd>
</dl>

## Commands

The ```run``` executable is a convenience script used to run commonly used commands in the Laravel application.

It supports the following commands:

```sh
# ARTISAN
# To run any artisan command
# The php service needs to be running for the following command to work

./run artisan COMMAND [ARGS]

# e.g.: ./run artisan migrate:fresh --seed
# e.g.: ./run artisan test


# COMPOSER
# To run any composer command in the php service
# The php service needs to be running for the following command to work

./run composer COMMAND [ARGS]

# e.g.: ./run composer require carbon/carbon


# YARN
# To run any yarn command for the laravel project

./run yarn COMMAND [ARGS]

# e.g.: ./run yarn watch-poll
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
        'http://selenium:[[SELENIUM_PORT]]/wd/hub',
        DesiredCapabilities::firefox()
            ->setCapability("acceptInsecureCerts", true)
    );
}

...
```

## FAQ

Visit [makeareadme](https://www.makeareadme.com) for a detailed explanation on creating readmes.
