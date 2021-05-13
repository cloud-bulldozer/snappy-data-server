# Data Server

Deploy an [ASGI](https://asgi.readthedocs.io/en/latest/introduction.html) server and API to receive and explore test results. When deployed you can access the server's current API at the `/docs` route.

## Setup

Create a local directory to store data posted to the server's host's file system.

```shell
$ mkdir "$HOME/data_server/results" -p
```

## Usage

### Overview

1. Create a means of communication between the containers.
    * Podman containers can easily communicate with `localhost` when they're in the same pod.
    * Docker containers can easily communicate over the default `bridge` network when each service is given a `network-alias`.

2. Start a Postgresql database service.

3. Add usernames and passwords. 
    * Assign username and password to the `FIRST_SUPERUSER` environment variables. Usernames must be a valid email regular expression, but do not have to be capable of receiving email.
    * Run the application's `inital_data.py` to seed the database with user accounts. 

4. Execute the deployment's `start` script to get the server running.

### Notes

* The bind mount volume is labeled as a shared directory with the host, `:z`, to persist results and facilitate integration with other tools on the host.

## Environment Variables

Define a `.env` with these environment variables.

### Data Server Configuration

---

#### DATA_SERVER_LOG_LVL
Default: `info`  
Data server log level. Current [Uvicorn server](https://www.uvicorn.org) **options:** *'critical', 'error', 'warning', 'info', 'debug', 'trace'.*

#### DATA_SERVER_PORT
Default: `7070`  
This application's service port.

#### DATA_SERVER_PUBLIC_HOST
Default: `localhost`  
URL to public host of data server.

#### DATA_SERVER_SECRET
Secret to encode passwords in database.

#### POSTGRES_PORT
Docker: Empty string  (i.e. `POSTGRES_PORT=`)  
Podman: `5432`  
Postgres service port. 

#### POSTGRES_SERVER
Docker: name of the database network alias, see `docker-compose.sh`.  
Podman: `localhost`  
Domain name, or IP address, hosting the postgres service.

### Postgres Service Configuration

---

#### POSTGRES_PASSWORD
Postgresql database super user password.

### Initial User Configuration

---

#### FIRST_SUPERUSER
Username for the first super user.

#### FIRST_SUPERUSER_PASSWORD
Password for the first super user.


### Podman Invocation

Create a `pod-compose.sh` script with:

```shell
#!/bin/bash

set -o allexport
source .env


data_server_img="quay.io/openshift-scale/snappy-data-server:2"
pod=snappy
pgvol=pgvol
db_name=pg_svc
webserver_name=snap-web


podman rm -f $db_name $webserver_name script
podman volume rm $pgvol
podman pod rm $pod
podman volume create $pgvol
podman pod create --name=$pod --publish $DATA_SERVER_PORT:$DATA_SERVER_PORT


podman run \
    --detach \
    --env-file=.env \
    --name=$db_name \
    --pod=$pod \
    --volume $pgvol:/var/lib/postgresql/data \
    postgres:13.1-alpine
    

podman run \
    --detach \
    --name script \
    --env POSTGRES_PORT=5432 \
    --env POSTGRES_SERVER=localhost \
    --env-file=.env \
    --pod=$pod \
    --rm \
    $data_server_img ./scripts/prestart


podman run \
    --detach \
    --env POSTGRES_PORT=5432 \
    --env POSTGRES_SERVER=localhost \
    --env-file=.env \
    --name=$webserver_name \
    --pod=$pod \
    --volume "$HOME/data_server/results:/data_server/app/app/results:z" \
    $data_server_img
```