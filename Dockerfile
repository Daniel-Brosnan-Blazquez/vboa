# Base the image on centos
FROM centos
MAINTAINER Daniel Brosnan Blázquez <daniel.brosnan@deimos-space.com>
RUN yum install -y epel-release

RUN yum install -y postgresql \
    python34 \
    python34-pip \
    python34-tkinter \
    gcc \
    python34-devel \
    pytest

RUN pip3 install pytest-cov \
    termcolor \
    coverage \
    before_after \
    Sphinx

# Environment Variables
ENV EBOA_RESOURCES_PATH /eboa/src

# expose port
EXPOSE 5000