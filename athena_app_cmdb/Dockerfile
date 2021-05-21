# pull official base image
FROM artifactory.cdk.com/dockerhub/python:3.9.5-alpine3.13 as backend

# expose the port
EXPOSE 8000

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app_registry.settings.prod

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir -p /opt/athena_app_cmdb/config /opt/node_modules
WORKDIR /opt/athena_app_cmdb

ARG requirements=requirements/prod.txt

# Copy in your requirements file
COPY requirements/ /opt/athena_app_cmdb/requirements/

# Installing client libraries and any other package you need
# These are packages that are needed during runtime
RUN apk add --update --no-cache python3 libpq bash expat-dev libffi curl py-pip

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

# download AWS RDS SSL certificate to /opt/athena_app_cmdb/etc
RUN mkdir -p /opt/athena_app_cmdb/etc \
    && cd /opt/athena_app_cmdb/etc \
    && wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem \
    && ln -s rds-combined-ca-bundle.pem db-rootca.pem

# copy project source code
COPY . /opt/athena_app_cmdb/

ENTRYPOINT ["/opt/athena_app_cmdb/scripts/entrypoint.sh"]


FROM backend as nginx-build
RUN export SECRET_KEY='SECRET_KEY' && /usr/local/bin/python manage.py collectstatic --no-input


FROM artifactory.cdk.com/dockerhub/nginx:1.20.0-alpine as nginx
RUN rm -rf /usr/share/nginx/html/* && rm /etc/nginx/conf.d/default.conf
COPY ./etc/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=nginx-build /opt/athena_app_cmdb/static /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
