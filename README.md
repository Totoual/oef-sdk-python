# OEFCore Python API

## Introduction
This is the python API for the OEFCore, allowing
 * registration of agents and services in the OEF
 * searching for agents and services in the OEF
 * constructing a direct communication channel with another agent


## Dependencies
    * CMake
    * C++ compiler: tested with GCC 7.3.0
    * Google Protocol Buffers: can be installed from https://github.com/protocolbuffers/protobuf,
        see https://github.com/protocolbuffers/protobuf/blob/master/src/README.md for installation
        details. Make sure to choose protobuf-all when downloading

## Installation
In order to install oef_python, run:
    python setup.py install
