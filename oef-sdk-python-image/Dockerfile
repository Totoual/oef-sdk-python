FROM ubuntu:18.04

USER root
WORKDIR /root/

RUN apt-get update && \
    apt-get install -y g++ && \ 
    apt-get install -y make &&\
    apt-get install -y git &&\
    apt-get install -y cmake

RUN apt-get install -y \
     libprotobuf-dev libprotoc-dev \
     protobuf-compiler  python-protobuf

RUN apt-get install -y python3-pip
RUN pip3 install pipenv
