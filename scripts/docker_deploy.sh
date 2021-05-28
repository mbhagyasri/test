#!/usr/bin/bash

###
#  This script is used to prepare the test environment for local development.  It is assuming the source code is specified
#  the path under APP_HOME.  This script is not used for actual dev/stage/prod deployment.
###
mkdir -p /docker/services/athena_app_cmdb /docker/data/athena_app_cmdb/logs /docker/gfs_data/athena_app_cmdb/postgresql \
            /docker/gfs_data/athena_app_cmdb/migrations /docker/gfs_data/athena_app_cmdb/config/ssl /docker/gfs_data/athena_app_cmdb/static_files

APP_NAME=athena_app_cmdb
APP_HOME=/docker/services/athena_app_cmdb
APP_ADDR=https://localhost:8000
export athena_app_cmdb_ADDR=$APP_ADDR
ENV_FILE=/docker/gfs_data/${APP_NAME}/config/${APP_NAME}.env
cd $APP_HOME
if [ ! -f "$ENV_FILE" ]; then
    cp ${APP_HOME}/env/${APP_NAME}.prod.env $ENV_FILE
    # Generate random password for DB
    PWD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9!*_' | fold -w 32 | head -n 1 )
    echo "SQL_PASSWORD=${PWD}" >> $ENV_FILE
    echo "POSTGRES_PASSWORD=${PWD}" >> $ENV_FILE
    SECRET_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1 )
    echo "SECRET_KEY=${SECRET_KEY}" >> $ENV_FILE
fi


