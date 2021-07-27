# Data Server

Deploy an [ASGI](https://asgi.readthedocs.io/en/latest/introduction.html) server and API to receive and explore test results. When deployed, you can access the server's current API at the `/docs` route.

## Setup

Create a local directory to store data posted to the server's host's file system.

```shell
mkdir "$HOME/data_server/results" -p
```

## Local Development

### Requirements

* minimum 600 MiB RAM
* Python ^3.7.1 ([translating caret requirements](https://python-poetry.org/docs/versions/))
* [poetry](https://python-poetry.org/docs/#installation)
* PostgreSQL service
* Current working directory is project root

```shell
poetry install --dev
```

### Environment Variable Configuration

Define a `.env` with these environment variables.

---

#### Data Server Configuration

* `DATA_SERVER_LOG_LVL`

    Default: `info`

    Data server log level. Current [Uvicorn server](https://www.uvicorn.org) **options:** *'critical', 'error', 'warning', 'info', 'debug', 'trace'.*

* `DATA_SERVER_PORT`

    Default: `7070`

    This application's service port.

* `DATA_SERVER_PUBLIC_HOST`

    Default: `localhost`

    URL to public host of data server.

* `DATA_SERVER_SECRET`

    Secret to encode passwords in database.

---

#### Postgres Service Configuration

* `POSTGRES_PORT`

    Docker: Empty string  (i.e. `POSTGRES_PORT=`)

    Podman: `5432`

    Postgres service port.

* `POSTGRES_SERVER`

    Docker: name of the database network alias, see `docker-compose.sh`.

    Podman: `localhost`

    Domain name, or IP address, hosting the postgres service.

* `POSTGRES_PASSWORD`

    Postgresql database super user password.

---

#### Initial User Configuration

* `FIRST_SUPERUSER`

    Username for the first super user, in the format of an e-mail.

* `FIRST_SUPERUSER_PASSWORD`

    Password for the first super user.

---

### Pruner Configuration

#### ENABLE_PRUNER

Var to enable or disable pruner

Configure the `pruner_config.toml` configuration file to add folders on which the pruner should be active. In the toml file you also need to set the days_to_live parameter, which will determine the number of days after which the files/folders in the path are pruned.

The pruner and server logs can be viewed by running the command `podman logs snap_web` on the machine/instance on which snappy server is deployed.

## Steps to create and run a new container image of snappy server

Make your changes in the snappy-data-server directory.

This will create a local podman image name `snappy`

```shell
podman build --tag snappy -f Dockerfile
```

In the same directory as `pod-compose.sh`, create a `.env` configuration file.

Full example

```shell
POSTGRES_PASSWORD=barfoo
DATA_SERVER_SECRET=secretfoobar
DATA_SERVER_LOG_LVL=info
DATA_SERVER_PUBLIC_HOST=localhost
DATA_SERVER_PORT=7070
FIRST_SUPERUSER=foo@bar.com
FIRST_SUPERUSER_PASSWORD=foobar
```

Start snappy server pod with the image you built locally.

```shell
./pod-compose.sh localhost/snappy
```

## Containerized Application Usage

### Overview

1. Configure `.env` for PostgreSQL service and Snappy server application.

2. Create a means of communication between the containers.
    * Podman containers can easily communicate with `localhost` when they're in the same pod.
    * Docker containers can easily communicate over the default `bridge` network when each service is given a `network-alias`.

3. Start a PostgreSQL database service.

4. Add usernames and passwords.
    * Assign username and password to the `FIRST_SUPERUSER` environment variables. Usernames must be a valid email regular expression, but do not have to be capable of receiving email.
    * Run the application's `inital_data.py` to seed the database with user accounts.

5. Execute the deployment's `start.sh` script to get the server running.

### Notes

* The bind mount volume is labeled as a shared directory with the host, `:z`, to persist results and facilitate integration with other tools on the host.

## Next step

Using the data server with the [data server CLI](https://github.com/cloud-bulldozer/data-server-cli)
