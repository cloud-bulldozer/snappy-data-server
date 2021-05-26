#! /bin/bash

sudo dnf install -y podman git perl-open.noarch python3-devel gcc libpq-devel python3.9-devel
git clone https://github.com/mfleader/snappy-data-server.git
sudo chown -R vagrant snappy-data-server
sudo chgrp -R vagrant snappy-data-server
cd snappy-data-server
git switch streaming


export POSTGRES_PASSWORD=secret
export DATA_SERVER_SECRET=secret
export DATA_SERVER_PUBLIC_HOST=localhost
export DATA_SERVER_PORT=7070
export DATA_SERVER_LOG_LVL=info
export FIRST_SUPERUSER=user@test.com
export FIRST_SUPERUSER_PASSWORD=secret
export POSTGRES_PORT=5432 
export POSTGRES_SERVER=localhost
export APP_ROOT=~/snappy-data-server
export PYTHONPATH=$APP_ROOT/app
mkdir $APP_ROOT/app/results 


python -m pip install wheel
python -m pip install -r requirements.txt


podman volume create pgvol
podman run \
    --detach \
    --env POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    --name=pg_svc \
    --publish 5432:5432 \
    --volume pgvol:/var/lib/postgresql/data \
    docker.io/library/postgres:13.1-alpine
    

$APP_ROOT/app/scripts/prestart.sh
$APP_ROOT/app/scripts/start.sh
