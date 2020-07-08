# Data Server

Deploy an [ASGI](https://asgi.readthedocs.io/en/latest/introduction.html) server and API to receive and explore test results. When deployed you can access the server's current API at the `/docs` route.

## Setup

Create a local directory to store data posted to the server's host's file system.

```shell
$ mkdir "$HOME/data_server/results" -p
```

## Usage

Use the host network, `--net=host`, for traffic to get from a remote client through the host to the container. The bind mount volume is labeled as a shared directory with the host, `:z`, to persist results and facilitate integration with other tools on the host.

```shell
$ podman run \
    --detach \
    --name=snappy \
    --net=host \
    --env DATA_SERVER_PUBLIC_HOST=localhost \
    --env DATA_SERVER_PORT=7070 \
    --env DATA_SERVER_LOG_LVL=info \
    --volume "$HOME/data_server/results:/data_server/app/results:z" \ 
    quay.io/openshift-scale/snappy-data-server
```

## Example

A simple script to show **snappy** being deployed locally and interacting with it's API.

```shell
./localhost-example
````

## Environment Variables

### DATA_SERVER_PUBLIC_HOST
Default: `localhost`  
URL to public host of data server.

### DATA_SERVER_PORT
Default: `7070`  
Service port.

### DATA_SERVER_LOG_LVL
Default: `info`  
Data server log level. Current [Uvicorn server](https://www.uvicorn.org) **options:** *'critical', 'error', 'warning', 'info', 'debug', 'trace'.
