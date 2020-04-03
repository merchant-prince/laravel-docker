#! /bin/sh

set -e

cron -f &

exec docker-php-entrypoint "${@}"
