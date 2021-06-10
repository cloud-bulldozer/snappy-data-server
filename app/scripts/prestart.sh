#! /bin/env sh

# wait for db to start
python $APP_ROOT/app/scripts/backend_prestart.py

# add initial data to db
python $APP_ROOT/app/scripts/initial_data.py
