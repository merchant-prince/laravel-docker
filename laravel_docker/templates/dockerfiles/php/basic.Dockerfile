FROM php:fpm

RUN apt-get update \
 && apt-get install -y cron composer sudo supervisor zip libpq-dev libzip-dev \
 && docker-php-ext-install bcmath pdo_pgsql pgsql pcntl zip \
 && docker-php-ext-configure pgsql \
 && docker-php-ext-configure zip \
 && apt autoremove \
 && rm -rf /var/lib/apt/lists/*

# Setup php.ini file
RUN cp "${PHP_INI_DIR}/php.ini-development" "${PHP_INI_DIR}/php.ini"

###
# Change the UID and GID of the www-data so that there are no permission
# conflicts on the files manipulated by the container on the host.
###

ARG USER_ID
ARG GROUP_ID

RUN userdel -f www-data && \
    if getent group www-data; \
    then \
      groupdel www-data; \
    fi && \
    groupadd -g ${GROUP_ID} www-data && \
    useradd -l -u ${USER_ID} -g www-data www-data && \
    install -d -m 0755 -o www-data -g www-data /home/www-data && \
    chown --changes \
          --silent \
          --no-dereference \
          --recursive \
          --from=33:33 \
          ${USER_ID}:${GROUP_ID} \
          /home/www-data

# Setup privileges for www-data to start cron
# @todo: add more restrictive perms
RUN echo "www-data ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

VOLUME [ "${PHP_INI_DIR}", "/etc/crontab", "/var/www/html" ]

USER www-data

# @todo: use gosu instead
CMD ["sudo", "/usr/bin/supervisord", "--configuration", "/etc/supervisor/conf.d/supervisord.conf"]
