# Base the image on Rocky Linux (Red hat compatible)
FROM rockylinux:9

ARG FLASK_APP
ARG UID_HOST_USER

USER root

RUN useradd -m -o -r -u $UID_HOST_USER boa

RUN yum install -y epel-release-9-10.el9

RUN yum install --allowerasing -y python3-3.9.25-3.el9_7.1 \
    python3-pip-21.3.1-1.el9 \
    python3-tkinter-3.9.25-3.el9_7.1 \
    gcc \
    python3-devel-3.9.25-3.el9_7.1 \
    npm \
    make-1:4.3-8.el9 \
    gcc-c++ \
    which-2.21-30.el9_6 \
    p7zip-16.02-31.el9 \
    unzip-6.0-59.el9 \
    less-590-6.el9 \
    cronie-1.5.7-15.el9 \
    libcurl-7.76.1-35.el9_7.3 \
    libcurl-devel-7.76.1-35.el9_7.3 \
    postgresql-devel-13.23-1.el9_7 \
    postgresql-13.23-2.el9_7 \
    openssl \
    docker \
    procps \
    glibc-langpack-en-2.34-231.el9_7.10 \
    redhat-rpm-config-210-1.el9

RUN yum install -y ruby-3.0.7-165.el9_5 \
    rubygem-bundler-2.2.33-165.el9_5 \
    ruby-devel-3.0.7-165.el9_5

# This solves the dependency of minArc/ORC with rexml which previously was coming with ruby
RUN gem install rexml

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

RUN echo "declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /resources_path/container.env; while true; do echo 'Trying to start the web server...'; gunicorn --certfile /resources_path/boa_certificate.pem --keyfile /resources_path/boa_key.pem --worker-tmp-dir /dev/shm -b 0.0.0.0:5001 -w 12 $FLASK_APP.wsgi:app --log-file /log/web_server -t 3600 --daemon; if [[ $? != 0 ]]; then echo 'Failed to start the web server...'; sleep 1; else echo 'Web server started! :D'; fi; SCRIPT_NAME="" VBOA_TEST=TRUE gunicorn --worker-tmp-dir /dev/shm -b 0.0.0.0:5000 -w 12 $FLASK_APP.wsgi:app --log-file /log/internal_web_server -t 3600; if [[ $? != 0 ]]; then echo 'Failed to start the web server...'; sleep 1; else echo 'Internal web server started! :D'; fi; done; sleep infinity" > /scripts/start_gunicorn.sh

RUN chmod u+x /scripts/start_gunicorn.sh

CMD ["/bin/bash", "-c", "/scripts/start_gunicorn.sh"]