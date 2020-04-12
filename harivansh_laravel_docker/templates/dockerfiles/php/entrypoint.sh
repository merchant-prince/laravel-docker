#! /bin/sh

set -e

# Check if the custom-php.ini file is in the additional .ini files array.
# If not, this means that the file was not mounted in the correct directory,
# which, in turn, means that the docker-compose PHP_INI_DIR (defined in the .env file)
# is not equal to the php service's PHP_INI_DIR.
if php -r "echo php_ini_scanned_files();" | grep -q "custom-php.ini"
then
    echo "Could not find the 'custom-php.ini' file in the additional .ini files array."
    echo "Please verify that the PHP_INI_DIR of the .env file is the same as the one defined in the php service."
    echo "If not, please change it so that it corresponds to the one defined in the php service."
    exit 1
fi

cron -f &

exec docker-php-entrypoint "${@}"
