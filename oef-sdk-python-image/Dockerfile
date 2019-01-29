FROM ubuntu:18.04

USER root
WORKDIR /root/


RUN apt-get update && \
    apt-get install -y g++ && \ 
    apt-get install -y make

RUN apt-get install -y \
     libprotobuf-dev libprotoc-dev \
     protobuf-compiler  python-protobuf

RUN apt-get install -y python3-pip

WORKDIR /work/
COPY ./ ./

RUN python3 setup.py install

RUN pip3 install -r requirements.txt 

RUN apt-get install -y git cmake

RUN python3 scripts/setup_test.py && \
    tox

WORKDIR ./docs/

RUN make html
