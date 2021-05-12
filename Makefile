SHA    := $(shell git describe --match=NeVeRmAtCh --always --abbrev=40 --dirty=*)
NAME   := athena_app_cmdb
TAG    := $(shell git log -1 --pretty=%H)
IMG    := ${NAME}:${TAG}
LATEST := ${NAME}:latest
VERSION := $(shell cat version.txt)
IMGVERSION := ${NAME}:${VERSION}

build:
	docker build -t ${IMG} athena_app_cmdb
	docker tag ${IMG} ${LATEST}
	docker tag ${IMG} ${IMGVERSION}

push:
	@docker push ${NAME}

login:
	@docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} docker.cdk.com:9015

start:
	docker-compose -f docker-compose-${BUILDENV}.yml start

stop:
	docker-compose -f docker-compose-${BUILDENV}.yml stop

up:
	docker-compose -f docker-compose-${BUILDENV}.yml up -d

down:
	docker-compose -f docker-compose-${BUILDENV}.yml down

restart-athena_app_cmdb:
	docker-compose -f docker-compose-${BUILDENV}.yml restart athena_app_cmdb

logs:
	docker-compose -f docker-compose-${BUILDENV}.yml logs

rmi:
	docker rmi $$(docker images -f dangling=true -q)

exec:
	docker-compose -f docker-compose-${BUILDENV}.yml exec athena_app_cmdb /bin/bash

exec-pg:
	docker-compose -f docker-compose-${BUILDENV}.yml exec athena_app_cmdb-postgres /bin/bash

setupdb:
	docker-compose -f docker-compose-${BUILDENV}.yml exec athena_app_cmdb sh -c "/usr/local/bin/python manage.py makemigrations athena_app_cmdb && /usr/local/bin/python manage.py migrate athena_app_cmdb && /usr/local/bin/python manage.py migrate"

collectstatic: 
	docker-compose -f docker-compose-${BUILDENV}.yml exec athena_app_cmdb sh -c "/usr/local/bin/python manage.py collectstatic --no-input"
