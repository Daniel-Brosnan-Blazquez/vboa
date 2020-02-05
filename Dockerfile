# Base the image on centos/postgresql-10-centos7
FROM centos/postgresql-10-centos7
MAINTAINER Daniel Brosnan Blázquez <daniel.brosnan@deimos-space.com>

ARG FLASK_APP
ARG UID_HOST_USER

USER root

RUN useradd -m -o -r -u $UID_HOST_USER boa

RUN yum install -y epel-release

RUN yum install -y postgresql-devel \
    python36 \
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
    libcurl-devel

RUN yum install -y rh-ruby25 \
    rh-ruby25-rubygem-bundler \
    rh-ruby25-ruby-devel

# Create folders for BOA
RUN mkdir /log
RUN mkdir /scripts
RUN mkdir /resources_path
RUN mkdir /datamodel
RUN mkdir /schemas
RUN mkdir /rboa_archive

# Create folders for ORC
RUN mkdir /orc
RUN mkdir /orc_packages
RUN mkdir /orc_config
RUN mkdir /minarc_root
RUN mkdir /inputs

# Change ownership to the boa user
RUN chown boa /log /scripts /resources_path /datamodel /schemas /rboa_archive /orc_packages /orc_config /minarc_root /inputs /orc

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
ENV MINARC_DATABASE_NAME s2boa_orc
ENV MINARC_DB_ADAPTER postgresql
ENV MINARC_DATABASE_USER root
ENV MINARC_DATABASE_PASSWORD 1mysql
ENV ORC_CONFIG /orc_config
ENV ORC_TMP /orc/tmp
ENV ORC_DATABASE_NAME s2boa_orc
ENV ORC_DB_ADAPTER postgresql
ENV ORC_DATABASE_USER root
ENV ORC_DATABASE_PASSWORD 1mysql
ENV POSTGRESQL_USER root
ENV POSTGRESQL_PASSWORD pass
ENV POSTGRESQL_DATABASE default

# Copy the environment variables to a file for later use of cron
RUN declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /resources_path/container.env

USER postgres
