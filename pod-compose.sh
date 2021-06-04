#!/bin/bash

set -o allexport
source .env


# assign first argument to data server image, otherwise use default
data_server_img=${1:-"quay.io/openshift-scale/snappy-data-server:2"}


podman rm -f pg_svc snap_web script
podman volume rm pgvol
podman pod rm snappy
podman volume create pgvol
podman pod create --name=snappy --publish $DATA_SERVER_PORT:$DATA_SERVER_PORT


podman run \
    --detach \
    --env-file=.env \
    --name=pg_svc \
    --pod=snappy \
    --volume pgvol:/var/lib/postgresql/data \
    postgres:13.1-alpine
    

podman run \
    --detach \
    --name script \
    --env POSTGRES_PORT=5432 \
    --env POSTGRES_SERVER=localhost \
    --env-file=.env \
    --pod=snappy \
    --rm \
    $data_server_img sh scripts/prestart.sh


podman run \
    --detach \
    --env POSTGRES_PORT=5432 \
    --env POSTGRES_SERVER=localhost \
    --env-file=.env \
    --name=snap_web \
    --pod=snappy \
    --volume "$HOME/data_server/results:/data_server/app/app/results:z" \
    $data_server_img


