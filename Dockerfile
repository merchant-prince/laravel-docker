FROM python:latest as test

LABEL maintainer=hello@harivan.sh

ARG USER
ARG GROUP

RUN mkdir /application \
 && chown ${USER}:${GROUP} /application

COPY --chown=${USER}:${GROUP} [ "harivansh_laravel_docker", "/application/harivansh_laravel_docker" ]
COPY --chown=${USER}:${GROUP} [ "tests", "/application/tests" ]
COPY --chown=${USER}:${GROUP} [ ".credentials", "LICENSE", "README.md", "requirements.txt", "setup.py", "/application/" ]

WORKDIR /application

VOLUME [ "/application/dist" ]

RUN pip install --upgrade pip \
 && pip install -r requirements.txt


FROM test as build

RUN pip install --upgrade setuptools wheel twine
