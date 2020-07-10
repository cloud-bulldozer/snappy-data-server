FROM docker.io/library/centos:8.2.2004

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
        python38-devel \
        python38 \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && ln -s /usr/bin/pip3 /usr/bin/pip \
    && dnf clean all \
    && pip install --requirement requirements.txt

WORKDIR ${APP_ROOT}/app

CMD ["/usr/bin/bash", "./scripts/start"]