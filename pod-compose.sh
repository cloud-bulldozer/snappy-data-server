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
podman pod create --name=$pod


podman run \
    --detach \
    --env-file=.env \
    --name=$db_name \
    --pod=$pod \
    --volume $pgvol:/var/lib/postgresql/data \
    postgres:12.3-alpine
    

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
    --publish ${DATA_SERVER_PORT}:${DATA_SERVER_PORT} \
    --volume "$HOME/data_server/results:/data_server/app/app/results:z" \
    $data_server_img