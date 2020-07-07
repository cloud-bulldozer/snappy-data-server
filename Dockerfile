FROM docker.io/library/centos:8.2.2004

LABEL maintainer="Matthew F Leader <mleader@redhat.com>"

ENV PATH=/root/.local/bin:$PATH \
    PIP_NO_CACHE_DIR=off \
    LANG=C.UTF-8
ENV APP_ROOT=/data_server
ENV PIPENV_PYTHON=python

RUN dnf install -y python38 \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && ln -s /usr/bin/pip3 /usr/bin/pip \
    && dnf clean all \
    && pip install pipenv

COPY ./app ${APP_ROOT}/app
COPY Pipfile ${APP_ROOT}/
COPY ./start.bash ${APP_ROOT}/start.bash
WORKDIR ${APP_ROOT}

RUN pipenv install --skip-lock

CMD ["/usr/bin/bash", "./start.bash"]