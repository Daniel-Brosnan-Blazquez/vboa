# Base the image on centos7
FROM centos:centos7
MAINTAINER Daniel Brosnan Blázquez <daniel.brosnan@deimos-space.com>

ARG FLASK_APP
ARG UID_HOST_USER

USER root

RUN useradd -m -o -r -u $UID_HOST_USER boa

RUN yum install -y epel-release

RUN yum install -y python36 \
    python36-pip \
    python36-tkinter \
    gcc \
    python36-devel \
    pytest \
    npm \
    centos-release-scl-rh \
    centos-release-scl \
    make \
    gcc-c++ \
    sqlite-devel \
    which \
    p7zip \
    unzip \
    less \
    cronie \
    libcurl \
    libcurl-devel \
    postgresql-devel \
    postgresql \
    openssl \
    docker

RUN yum install -y rh-ruby27 \
    rh-ruby27-rubygem-bundler \
    rh-ruby27-ruby-devel \
    rh-postgresql10-postgresql-devel

RUN yum update -y

RUN pip3 install wheel

# Create folders for BOA
RUN mkdir /log
RUN mkdir /scripts
RUN mkdir /resources_path
RUN mkdir /datamodel
RUN mkdir /schemas
RUN mkdir /rboa_archive
RUN mkdir /metrics
RUN mkdir /metrics_to_publish

# Create folders for ORC
RUN mkdir /orc
RUN mkdir /orc_packages
RUN mkdir /minarc_root
RUN mkdir /inputs

# Change ownership to the boa user
RUN chown boa /log /scripts /resources_path /datamodel /schemas /rboa_archive /metrics /metrics_to_publish /orc_packages /minarc_root /inputs /orc

USER boa

# Environment Variables for BOA
ENV EBOA_RESOURCES_PATH /resources_path
ENV EBOA_LOG_PATH /log
ENV EBOA_SCHEMAS_PATH /schemas
ENV FLASK_APP $FLASK_APP
ENV FLASK_ENV development
ENV LC_ALL en_US.utf-8
ENV LANG en_US.utf-8
ENV PATH="${PATH}:/scripts"
ENV RBOA_ARCHIVE_PATH="/rboa_archive"

# expose port
EXPOSE 5000

# Environment Variables for ORC
ENV MINARC_ARCHIVE_ROOT /minarc_root
ENV MINARC_ARCHIVE_ERROR /minarc_root/.errors
ENV MINARC_DATABASE_NAME minarc_orc_db
ENV MINARC_DB_ADAPTER postgresql
ENV MINARC_DATABASE_USER minarc_orc
ENV ORC_TMP /orc/tmp
ENV ORC_DATABASE_NAME minarc_orc_db
ENV ORC_DB_ADAPTER postgresql
ENV ORC_DATABASE_USER minarc_orc

RUN echo "source scl_source enable rh-ruby27; declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /resources_path/container.env; while true; do echo 'Trying to start the web server...'; gunicorn --certfile /resources_path/boa_certificate.pem --keyfile /resources_path/boa_key.pem --worker-tmp-dir /dev/shm -b 0.0.0.0:5001 -w 12 $FLASK_APP.wsgi:app --log-file /log/web_server -t 3600 --daemon; if [[ $? != 0 ]]; then echo 'Failed to start the web server...'; sleep 1; else echo 'Web server started! :D'; fi; SCRIPT_NAME="" VBOA_TEST=TRUE gunicorn --worker-tmp-dir /dev/shm -b 0.0.0.0:5000 -w 12 $FLASK_APP.wsgi:app --log-file /log/internal_web_server -t 3600; if [[ $? != 0 ]]; then echo 'Failed to start the web server...'; sleep 1; else echo 'Internal web server started! :D'; fi; done; sleep infinity" > /scripts/start_gunicorn.sh

RUN chmod u+x /scripts/start_gunicorn.sh

CMD ["/bin/bash", "-c", "/scripts/start_gunicorn.sh"]