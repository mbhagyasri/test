### build up swagger
FROM artifactory.cdk.com/dockerhub/node:12-alpine AS node-tmp
RUN mkdir -p /opt/athena_app_cmdb && chown -R node:node /opt/athena_app_cmdb
WORKDIR /opt/athena_app_cmdb
COPY ./athena_app_cmdb/ui /opt/athena_app_cmdb/athena_app_cmdb/ui
RUN npm install -g @apidevtools/swagger-cli openapi-types@>=7 \
    && swagger-cli bundle --outfile=/opt/athena_app_cmdb/athena_app_cmdb/ui/openapi.yaml /opt/athena_app_cmdb/athena_app_cmdb/ui/openapi_ref.yaml

# pull official base image
FROM artifactory.cdk.com/dockerhub/python:3.9.5-alpine3.13 as backend

# expose the port
EXPOSE 8000

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app_registry.settings.prod

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir -p /opt/athena_app_cmdb/config /opt/athena_app_cmdb/etc
WORKDIR /opt/athena_app_cmdb

ARG requirements=requirements/prod.txt

# Copy in your requirements file
COPY requirements/ /opt/athena_app_cmdb/requirements/
# Installing client libraries and any other package you need
# These are packages that are needed during runtime
RUN apk add --update --no-cache python3 libpq bash expat-dev libffi curl py-pip ca-certificates
# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements file, if needed.
RUN set -ex \
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
    && pip install -U pip \
    && pip install --no-cache-dir -r $requirements \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps
# copy project source code
COPY . /opt/athena_app_cmdb/
COPY --from=node-tmp /opt/athena_app_cmdb/athena_app_cmdb/ui/openapi.yaml /openapi.yaml

# download AWS RDS SSL certificate to /opt/athena_app_cmdb/etc
RUN cd /opt/athena_app_cmdb/etc \
    && wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem \
    && cp /opt/athena_app_cmdb/etc/rds-combined-ca-bundle.pem /usr/local/share/ca-certificates/rds-combined-ca-bundle.pem \
    && update-ca-certificates
RUN chmod +x /opt/athena_app_cmdb/scripts/entrypoint.sh
ENTRYPOINT ["/opt/athena_app_cmdb/scripts/entrypoint.sh"]

FROM backend as nginx-build
RUN export SECRET_KEY='SECRET_KEY' && /usr/local/bin/python manage.py collectstatic --no-input


FROM artifactory.cdk.com/dockerhub/nginx:1.20.0-alpine as nginx
RUN rm -rf /usr/share/nginx/html/* && rm /etc/nginx/conf.d/default.conf
COPY ./etc/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=nginx-build /opt/athena_app_cmdb/static /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]


FROM artifactory.cobalt.com/athena/athena-platform/tooling-base:latest as installer
COPY ["./helm", "./helm"]
COPY ["./scripts", "./scripts"]
RUN shellcheck ./scripts/install.sh
RUN chmod +x ./scripts/install.sh
ENTRYPOINT [ "./scripts/install.sh" ]


