### build up swagger
FROM artifactory.cdk.com/dockerhub/node:12-alpine AS node-tmp
RUN mkdir -p /opt/athena_app_cmdb && chown -R node:node /opt/athena_app_cmdb
WORKDIR /opt/athena_app_cmdb
COPY ./athena_app_cmdb/ui /opt/athena_app_cmdb/athena_app_cmdb/ui
RUN npm install -g @apidevtools/swagger-cli openapi-types@>=7 \
    && swagger-cli bundle --outfile=/opt/athena_app_cmdb/athena_app_cmdb/ui/openapi.yaml /opt/athena_app_cmdb/athena_app_cmdb/ui/openapi_ref.yaml

# pull official base image
FROM artifactory.cdk.com/dockerhub/python:3.9.5-alpine3.13 as base
# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir -p /opt/athena_app_cmdb/config /opt/athena_app_cmdb/etc
WORKDIR /opt/athena_app_cmdb
# Installing client libraries and any other package you need
# These are packages that are needed during runtime
# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements file, if needed.
RUN set -ex \
    && apk add --update --no-cache python3 libpq bash expat-dev libffi curl py-pip ca-certificates postgresql-client graphviz ttf-freefont openldap-clients \
    && apk add --update --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-client \
            python3-dev \
            build-base \
            postgresql-dev \
            libffi-dev \
            openssl-dev \
            cargo \
            openldap-dev \
            graphviz-dev \
    && pip install -U pip \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps

# unit test stage
FROM base as unittest
# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app_registry.settings.test
# Copy in your requirements file
COPY requirements/ /opt/athena_app_cmdb/requirements/
ARG requirements=requirements/dev.txt
# copy project source code
COPY . /opt/athena_app_cmdb/
ENV SECRET_KEY='SECRET_KEY'
# generate ERD file
RUN pip install --no-cache-dir -r $requirements \
    && apk del .build-deps \
    && export SECRET_KEY='SECRET_KEY' \
    && /usr/local/bin/python manage.py graph_models athena_app_cmdb -g --pygraphviz -o athena_app_cmdb/static/img/athena_app_cmdb_erd.png \
    && python manage.py makemigrations athena_app_cmdb\
    && python manage.py migrate athena_app_cmdb \
    && python manage.py migrate \
    && python manage.py test athena_app_cmdb.test

# real backend
FROM base as backend
# expose the port
EXPOSE 8000
# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app_registry.settings.prod
# Copy in your requirements file
COPY requirements/ /opt/athena_app_cmdb/requirements/
ARG requirements=requirements/prod.txt
RUN pip install --no-cache-dir -r $requirements \
    && apk del .build-deps
# copy project source code
COPY . /opt/athena_app_cmdb/
COPY --from=node-tmp /opt/athena_app_cmdb/athena_app_cmdb/ui/openapi.yaml /openapi.yaml
# generate ERD file
RUN export SECRET_KEY='SECRET_KEY' && /usr/local/bin/python manage.py graph_models athena_app_cmdb -g --pygraphviz -o  \
    athena_app_cmdb/static/img/athena_app_cmdb_erd.png
# download AWS RDS SSL certificate to /opt/athena_app_cmdb/etc
RUN wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem \
    && cp /opt/athena_app_cmdb/rds-combined-ca-bundle.pem /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem \
    && update-ca-certificates \
    && mv /opt/athena_app_cmdb/rds-combined-ca-bundle.pem /opt/athena_app_cmdb/etc/rds-combined-ca-bundle.pem \
    && chmod +x /opt/athena_app_cmdb/scripts/entrypoint.sh
ENTRYPOINT ["/opt/athena_app_cmdb/scripts/entrypoint.sh"]

FROM backend as nginx-build
RUN export SECRET_KEY='SECRET_KEY' && /usr/local/bin/python manage.py collectstatic --no-input


FROM artifactory.cdk.com/dockerhub/nginx:1.20.0-alpine as nginx
RUN rm -rf /usr/share/nginx/html/* && rm /etc/nginx/conf.d/default.conf
COPY ./etc/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=nginx-build /opt/athena_app_cmdb/static /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]


FROM artifactory.cdk.com/docker-local/athena/athena-platform/tooling-base:latest as installer
COPY ["./helm", "./helm"]
COPY ["./scripts", "./scripts"]
RUN shellcheck ./scripts/install.sh
RUN chmod +x ./scripts/install.sh
ENTRYPOINT [ "./scripts/install.sh" ]


