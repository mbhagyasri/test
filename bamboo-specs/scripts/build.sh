#!/bin/bash

set -e

### create .artifact file
echo "container_tag=${container_tag}" > .artifact

# change work directory
cd athena_app_cmdb

# build nginx container
docker build \
    -t artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb-nginx:latest \
    -t artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb-nginx:${container_tag} \
    --target=nginx \
    .

# build backend container
docker build \
    -t artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb:latest \
    -t artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb:${container_tag} \
    --target=backend \
    .

# build installer
docker build \
    -t artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb-install:latest \
    -t artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb-install:${container_tag} \
    --target=installer \
    .

docker push artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb:${container_tag}
docker push artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb:latest

docker push artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb-nginx:${container_tag}
docker push artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb-nginx:latest

docker push artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb-install:${container_tag}
docker push artifactory.cobalt.com/athena/athena-platform/athena-app-cmdb-install:latest

# END
