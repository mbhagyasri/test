#!/bin/bash

OS=$(uname)
BUILDENV=$OS

for i in "$@"; do
  case $i in
    -b=*|--build-env=*)
      BUILDENV="${i#*=}"
      shift # past argument=value
      ;;
    *)
      # unknown option
      ;;
  esac
done

DOCKER_COMPOSE_FILE_SOURCE=docker-compose-prod.yml
DOCKER_COMPOSE_FILE_TARGET=docker-compose-${BUILDENV}.yml
LOCAL_VOLUME_PATH=~/vol-appregv2-docker
DEPLOY_DOCKER_FILE_SOURCE=scripts/docker_deploy.sh
DEPLOY_DOCKER_FILE_TARGET=scripts/docker_deploy_${BUILDENV}.sh
PROJECT_ROOT_DIR=$(PWD)
APP_NAME=athena_app_cmdb
ENV_FILE=${LOCAL_VOLUME_PATH}/gfs_data/${APP_NAME}/config/${APP_NAME}.env

# Start clean
echo "Starting fresh on build environment: ${BUILDENV}"
if [ -f "$DOCKER_COMPOSE_FILE_TARGET" ]
then 
    echo "Cleaning up $DOCKER_COMPOSE_FILE_TARGET"
    rm $DOCKER_COMPOSE_FILE_TARGET
fi
if [ -f $ENV_FILE ] 
then
    echo "Cleaning up $ENV_FILE"
    rm -rf $ENV_FILE
fi
if [ -f "$DEPLOY_DOCKER_FILE_TARGET" ]
then
    echo "Cleaning up $DEPLOY_DOCKER_FILE_TARGET"
    rm $DEPLOY_DOCKER_FILE_TARGET
fi

# Copy the docker-compose file specific to OS
echo "Saving $DOCKER_COMPOSE_FILE_SOURCE as $DOCKER_COMPOSE_FILE_TARGET"
cp $DOCKER_COMPOSE_FILE_SOURCE $DOCKER_COMPOSE_FILE_TARGET

# Cop the docker_deplpoy.sh to be environment specific
echo "Saving $DEPLOY_DOCKER_FILE_SOURCE as $DEPLOY_DOCKER_FILE_TARGET"
cp $DEPLOY_DOCKER_FILE_SOURCE $DEPLOY_DOCKER_FILE_TARGET
echo "Setting executable permissions on $DEPLOY_DOCKER_FILE_TARGET"
chmod +x $DEPLOY_DOCKER_FILE_TARGET

# Create local volume directory in user home folder
echo "Creating local volumes on $LOCAL_VOLUME_PATH"
mkdir -p $LOCAL_VOLUME_PATH
chmod +x $LOCAL_VOLUME_PATH

if [ $OS == "Darwin" ]
then
    # Change volumes in docker-compose to use local setup
    echo "Updating the postgres configuration"
    sed -i "" "s|/docker/gfs_data/athena_app_cmdb/postgresql|/docker/gfs_data/athena_app_cmdb/postgresql/data|" $DOCKER_COMPOSE_FILE_TARGET
    sed -i "" "s|- /docker/gfs_data/athena_app_cmdb/config/postgresql.conf:/etc/postgresql.conf| |" $DOCKER_COMPOSE_FILE_TARGET
    sed -i "" "s|config_file=/etc/postgresql.conf|config_file=/var/lib/postgresql/data/postgresql.conf|" $DOCKER_COMPOSE_FILE_TARGET
    # Change the postgres path in the docker-compose
    echo "Replacing volume paths to use local volume paths on ${LOCAL_VOLUME_PATH}"
    sed -i "" "s|/docker|${LOCAL_VOLUME_PATH}|" $DOCKER_COMPOSE_FILE_TARGET
    # Change APP_HOME to current directory in docker_deploy.sh
    echo "Setting the APP_HOME to the project root directory"
    sed -i "" "s|APP_HOME=/docker/services/athena_app_cmdb|APP_HOME=${PROJECT_ROOT_DIR}|" $DEPLOY_DOCKER_FILE_TARGET
    # Change environment specific docker_deploy.sh to use local volumes
    echo "Replacing volume paths to use local volume paths as $LOCAL_VOLUME_PATH on $DEPLOY_DOCKER_FILE_TARGET"
    sed -i "" "s|/docker|$LOCAL_VOLUME_PATH|g" $DEPLOY_DOCKER_FILE_TARGET
else
    # Change volumes in docker-compose to use local setup
    echo "Updating the postgres configuration"
    sed -i "s|/docker/gfs_data/athena_app_cmdb/postgresql|/docker/gfs_data/athena_app_cmdb/postgresql/data|" $DOCKER_COMPOSE_FILE_TARGET
    sed -i "s|- /docker/gfs_data/athena_app_cmdb/config/postgresql.conf:/etc/postgresql.conf| |" $DOCKER_COMPOSE_FILE_TARGET
    sed -i "s|config_file=/etc/postgresql.conf|config_file=/var/lib/postgresql/data/postgresql.conf|" $DOCKER_COMPOSE_FILE_TARGET
    # Change the postgres path in the docker-compose
    echo "Replacing volume paths to use local volume paths on ${LOCAL_VOLUME_PATH}"
    sed -i "s|/docker|${LOCAL_VOLUME_PATH}|" $DOCKER_COMPOSE_FILE_TARGET
    # Change APP_HOME to current directory in docker_deploy.sh
    echo "Setting the APP_HOME to the project root directory"
    sed -i "s|APP_HOME=/docker/services/athena_app_cmdb|APP_HOME=${PROJECT_ROOT_DIR}|" $DEPLOY_DOCKER_FILE_TARGET
    # Change environment specific docker_deploy.sh to use local volumes
    echo "Replacing volume paths to use local volume paths as $LOCAL_VOLUME_PATH on $DEPLOY_DOCKER_FILE_TARGET"
    sed -i "s|/docker|$LOCAL_VOLUME_PATH|g" $DEPLOY_DOCKER_FILE_TARGET
fi

# Run the docker_deploy.sh to get environment variables created
echo "Run the script $DEPLOY_DOCKER_FILE_TARGET"
sh $DEPLOY_DOCKER_FILE_TARGET

if [ ! -f $ENV_FILE ]
then
    echo "File $ENV_FILE not found. Failing safely!"
    exit 1
fi

# Setup environment variables for postgres 
echo "Removing the generated/random passwords from $ENV_FILE"
if [ $OS == "Darwin" ]
then
    sed -i "" "/SQL_PASSWORD=/d" $ENV_FILE
    sed -i "" "/POSTGRES_PASSWORD=/d" $ENV_FILE
    sed -i "" "/SECRET_KEY=/d" $ENV_FILE
else
    sed -i "/SQL_PASSWORD=/d" $ENV_FILE
    sed -i "/POSTGRES_PASSWORD=/d" $ENV_FILE
    sed -i "/SECRET_KEY=/d" $ENV_FILE
fi

echo "Setting the default postgres passwords in $ENV_FILE"
echo "SQL_PASSWORD=postgres" >> $ENV_FILE
echo "POSTGRES_PASSWORD=postgres" >> $ENV_FILE
echo "SECRET_KEY=secret" >> $ENV_FILE
echo "PG_SSL_MODE=disable" >> $ENV_FILE

# Build the docker container
cd athena_app_cmdb
echo "Build the container athena_app_cmdb"
docker build -t athena_app_cmdb --target=backend .
cd ..

# Run the docker compose
echo "Running the docker-compose up"
make up BUILDENV=$BUILDENV
# If "make" command fails comment the above make line and uncomment below docker-compose line, usually happens on windows
# docker-compose -f docker-compose-${BUILDENV}.yml up -d

# Run the migrations
make setupdb BUILDENV=$BUILDENV
# If "make" command fails comment the above make lin and uncomment below docker-compose line, usually happens on windows
# docker-compose -f docker-compose-${BUILDENV}.yml exec athena_app_cmdb sh -c "/usr/local/bin/python manage.py makemigrations athena_app_cmdb && /usr/local/bin/python manage.py migrate athena_app_cmdb && /usr/local/bin/python manage.py migrate"