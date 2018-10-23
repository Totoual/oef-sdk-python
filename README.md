# OEFCore Python API

## Introduction
This is the python API for the OEFCore, allowing
 * registration of agents and services in the OEF
 * searching for agents and services in the OEF
 * constructing a direct communication channel with another agent


## Dependencies

- [Google Protocol Buffers](https://developers.google.com/protocol-buffers/) compiler. You can install it in several  ways, depending on your platform:

  - On Debian-based (e.g. Ubuntu):
        
        sudo apt-get install protobuf-compiler
  - You can do it manually by checking the [release page](https://github.com/protocolbuffers/protobuf/releases) and 
by choosing the release for your platform. The name format is `protoc-$(VERSION)-$(PLATFORM).zip` 
(e.g. for Windows look at `protoc-$(VERSION)-win32.zip`).
  - [Compile from source](https://github.com/protocolbuffers/protobuf/blob/master/src/README.md#c-installation---windows).

    
## Installation
In order to install oef_python, run:

    python setup.py install
