FROM docker.io/library/python:3.9.5

LABEL maintainer="Matthew F Leader <mleader@redhat.com>"

ENV PATH=/root/.local/bin:$PATH \
    LANG=C.UTF-8
ENV APP_ROOT=/data_server
ENV PYTHONPATH=${APP_ROOT}/app

RUN mkdir ${APP_ROOT}

COPY ./app ${APP_ROOT}/app/
COPY requirements.txt ${APP_ROOT}/

WORKDIR ${APP_ROOT}

# need psycopg2 for sqlalchemy to create db relations
# psycopg2 dependencies:
#   gcc, libpq-devel

RUN apt-get update && \
    apt-get install --yes \
        gcc \
        libpq-dev \
    && pip install --requirement requirements.txt

WORKDIR ${APP_ROOT}/app

CMD ["/bin/sh", "./scripts/start.sh"]