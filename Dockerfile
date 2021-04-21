FROM quay.io/fedora/fedora:34

LABEL maintainer="Matthew F Leader <mleader@redhat.com>"

ENV PATH=/root/.local/bin:$PATH \
    LANG=C.UTF-8
ENV APP_ROOT=/data_server
ENV PYTHONPATH=${APP_ROOT}/app

COPY ./app ${APP_ROOT}/app/
COPY requirements.txt ${APP_ROOT}/

WORKDIR ${APP_ROOT}

# need psycopg2 for sqlalchemy to create db relations
# psycopg2 dependencies:
#   gcc, libpq-devel

RUN dnf install -y \
        gcc \
        libpq-devel \
        python3.9-devel --nogpgcheck \
    && dnf clean all --nogpgcheck \
    && pip install --requirement requirements.txt

WORKDIR ${APP_ROOT}/app

CMD ["/usr/bin/bash", "./scripts/start"]
