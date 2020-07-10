#! /bin/bash

set -o allexport
source .env


data_server_img="quay.io/openshift-scale/snappy-data-server:2"
net=snappy
pgvol=pgvol
db_name=pg_svc
webserver_name=snap-web


docker network create $net
docker volume create $pgvol
docker rm -f $db_name $webserver_name
docker volume rm $pgvol


docker run \
    --detach \
    --env-file=.env \
    --name=$db_name \
    --net=$net \
    --network-alias=$db_name \
    --volume $pgvol:/var/lib/postgresql/data \
    postgres:12.3-alpine


docker run \
    --detach \
    --env POSTGRES_PORT= \
    --env POSTGRES_SERVER=$db_name \
    --env-file=.env \
    --net=$net \
    --rm \
    $data_server_img ./scripts/prestart


docker run \
    --detach \
    --env POSTGRES_PORT= \
    --env POSTGRES_SERVER=$db_name \
    --env-file=.env \
    --name=$webserver_name \
    --net=$net \
    --publish ${DATA_SERVER_PORT}:${DATA_SERVER_PORT} \
    --volume "$HOME/data_server/results:/data_server/app/app/results:z" \
    $data_server_img