.. _install:

Installation
============

For now, we only support installation from source.

Protobuffer Compiler
--------------------

The ``oef`` package requires that the `Google Protocol Buffers <https://developers.google.com/protocol-buffers/>`_
compiler is installed on your local machine.

In order to check if you already have it, run:

::

  protoc


If you get ``Missing input file.``, then you have already it.

Otherwise, you can install it in several  ways, depending on your platform:

* On Debian-based (e.g. Ubuntu):

::

  sudo apt-get install protobuf-compiler


* You can do it manually by checking the `release page <https://github.com/protocolbuffers/protobuf/releases>`_ and
  by choosing the release for your platform.
  The name format is ``protoc-$(VERSION)-$(PLATFORM).zip`` (e.g. for Windows look at ``protoc-$(VERSION)-win32.zip``).

* `Compile from source <https://github.com/protocolbuffers/protobuf/blob/master/src/README.md#c-installation---windows>`_.

Install the package
--------------------

Follow these steps:

* Clone the repository:

::

  git clone https://github.com/uvue-git/OEFCorePython.git --recursive && cd OEFCorePython/


* Install the package:

::

  python setup.py install

