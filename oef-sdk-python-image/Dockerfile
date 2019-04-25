FROM ubuntu:18.04

USER root
WORKDIR /root/

RUN apt-get update && \
    apt-get install -y g++ && \ 
    apt-get install -y make &&\
    apt-get install -y build-essential &&\
    apt-get install -y git &&\
    apt-get install -y cmake &&\
    apt-get install -y curl &&\
    apt-get install -y libssl-dev &&\
    apt-get install -y zlib1g-dev &&\
    apt-get install -y libbz2-dev &&\
    apt-get install -y libreadline-dev &&\
    apt-get install -y libsqlite3-dev &&\ 
    apt-get install -y libffi-dev

RUN apt-get install -y python3-pip python3-dev
 
RUN apt-get install -y tox

# install pipenv
ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN python3 -m pip install pipenv

RUN apt-get install -y protobuf-compiler

RUN mkdir /source
COPY . /source
WORKDIR /source
