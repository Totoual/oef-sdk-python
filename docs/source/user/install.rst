.. _install:

Installation
============

For now, we only support installation from source.

Protobuf Compiler
-----------------

The ``oef`` package requires that the `Google Protocol Buffers <https://developers.google.com/protocol-buffers/>`_
compiler is installed on your local machine (version >= 2.0.0).

In order to check if you already have it, run:

::

  protoc


If you get ``Missing input file.``, then you have already it.

Otherwise, you can install it in several  ways, depending on your platform.

* On Debian-based (e.g. Ubuntu):

::


Linux (Ubuntu)
~~~~~~~~~~~~~~

* Using the package manager:

.. code-block:: bash

  sudo apt-get install protobuf-compiler

* From the release

.. code-block:: bash

  PROTOC_ZIP=protoc-3.3.0-linux-x86_64.zip
  curl -OL https://github.com/google/protobuf/releases/download/v3.3.0/$PROTOC_ZIP
  sudo unzip -o $PROTOC_ZIP -d /usr/local bin/protoc
  rm -f $PROTOC_ZIP


.. code-block:: bash

  sudo apt-get install protobuf-compiler
  git clone https://github.com/uvue-git/OEFCorePython.git --recursive
  cd OEFCorePython/
  python setup.py install

For other platforms and other details, please follow the installation guide: :ref:`install`.

Mac OS X
~~~~~~~~

* If you have `Homebrew <https://brew.sh/>`_, just run:

.. code-block:: bash

  brew install protobuf

* Alternatively, run the following commands:

.. code-block:: bash

  PROTOC_ZIP=protoc-3.0.0-osx-x86_64.zip
  curl -OL https://github.com/google/protobuf/releases/download/v3.0.0/$PROTOC_ZIP
  sudo unzip -o $PROTOC_ZIP -d /usr/local bin/protoc
  rm -f $PROTOC_ZIP


Other platforms
~~~~~~~~~~~~~~~

You can do it manually by checking the `release page <https://github.com/protocolbuffers/protobuf/releases>`_ and
by choosing the release for your platform.
The name format is ``protoc-$(VERSION)-$(PLATFORM).zip`` (e.g. for Windows look at ``protoc-$(VERSION)-win32.zip``).

Alternatively, you can
`Compile from source <https://github.com/protocolbuffers/protobuf/blob/master/src/README.md#c-installation---windows>`_.



Install ``oef``
--------------------

To install the Python package ``oef``, follow these steps:

* Clone the repository:

::

  git clone https://github.com/uvue-git/OEFCorePython.git --recursive && cd OEFCorePython/


* Install the package:

::

  python setup.py install

