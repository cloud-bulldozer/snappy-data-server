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


### Steps to create and run a new podman image of snappy server: 

Make your changes in the snappy-data-server directory.


This will create a local podman image name `snappy`

  podman build --tag snappy -f Dockerfile
  
In the same directory as `pod-compose.sh`, create a `.env` configuration file.

This will start the snappy server with any new local changes.
  
  ./pod-compose.sh localhost/snappy


## Known Issues

The application will not work if you create a policy that restricts its process to less than 600 MB. 600 MB reserves 100 MB for the server, and 500 MB for file chunking.


