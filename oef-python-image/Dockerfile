FROM ubuntu:16.04

USER root
WORKDIR /root/

# use python3
RUN alias python=python3
RUN echo 'alias python=python3' >> ~/.bashrc

# update
RUN apt-get update

# install python-related apt-get pkgs
RUN apt-get -y install python3-pip
RUN alias pip=pip3
RUN echo 'alias pip=pip3' >> ~/.bashrc
# to avoid locale.Error: unsupported locale setting
RUN export LC_ALL=C
RUN echo 'export LC_ALL=C' >> ~/.bashrc

# install python-related pip pkgs
RUN pip3 install aiohttp ipython setuptools

# install protocol buffers
RUN apt-get -y install libprotobuf-dev libprotoc-dev \
                       libprotobuf9v5 libprotobuf-lite9v5 \
                       protobuf-compiler  python-protobuf
RUN pip3 install protobuf

# install dev tools
RUN apt-get -y install git cmake

# get OEFCorePython and install it
WORKDIR /work
COPY . /work
RUN cd ./oef/protos/ && make
RUN python3 setup.py develop

WORKDIR ./examples/

