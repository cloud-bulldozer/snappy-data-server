#! /bin/env sh

# wait for db to start
python $APP_ROOT/app/scripts/backend_prestart.py

uvicorn \
    --host "0.0.0.0" \
    --log-level $DATA_SERVER_LOG_LVL \
    --port $DATA_SERVER_PORT \
    --reload \
    app.main:app
