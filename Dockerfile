# Base the image on centos
FROM centos
MAINTAINER Daniel Brosnan Blázquez <daniel.brosnan@deimos-space.com>

ARG FLASK_APP

RUN yum install -y epel-release

RUN yum install -y postgresql \
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
    less

RUN yum install -y rh-ruby25 \
    rh-ruby25-rubygem-bundler \
    rh-ruby25-ruby-devel

RUN scl enable rh-ruby25 bash

# Create folders for BOA
RUN mkdir /log
RUN mkdir /scripts
RUN mkdir /resources_path
RUN mkdir /orc_packages
RUN mkdir /schemas

# Create folders for ORC
RUN mkdir /orc_config
RUN mkdir /minarc_root
RUN mkdir /inputs
RUN mkdir /datamodel

# Environment Variables for BOA
ENV EBOA_RESOURCES_PATH /resources_path
ENV EBOA_LOG_PATH /log
ENV EBOA_SCHEMAS_PATH /schemas
ENV FLASK_APP $FLASK_APP
ENV FLASK_ENV development
ENV LC_ALL en_US.utf-8
ENV LANG en_US.utf-8
ENV PATH="${PATH}:/scripts"

# expose port
EXPOSE 5000

# Environment Variables for ORC
ENV MINARC_ARCHIVE_ROOT /minarc_root
ENV MINARC_ARCHIVE_ERROR /minarc_root/.errors
ENV MINARC_DATABASE_NAME /orc/minarc_inventory
ENV MINARC_DB_ADAPTER sqlite3
ENV MINARC_DATABASE_USER root
ENV MINARC_DATABASE_PASSWORD 1mysql
ENV ORC_CONFIG /orc_config
ENV ORC_TMP /orc/tmp
ENV ORC_DATABASE_NAME /orc/orc_inventory
ENV ORC_DB_ADAPTER sqlite3
ENV ORC_DATABASE_USER root
ENV ORC_DATABASE_PASSWORD 1mysql