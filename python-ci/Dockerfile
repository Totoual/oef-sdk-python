FROM ubuntu:18.04

USER root

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python && \
    apt-get install -y python-pip && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip

RUN python3 -m pip install --upgrade pip

RUN mkdir build
COPY . /build
RUN cd /build

WORKDIR /build

ENTRYPOINT []