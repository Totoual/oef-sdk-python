.. _quickstart:

Quickstart
==========

This is a quick start guide, for the eager users.

Install
-------

For Linux (Ubuntu):

.. code-block:: bash

  sudo apt-get install protobuf-compiler
  git clone https://github.com/uvue-git/OEFCorePython.git --recursive
  cd OEFCorePython/
  python setup.py install

For other platforms and other details, please follow the installation guide: :ref:`install`.


Run a OEF Node
~~~~~~~~~~~~~~~~

.. code-block:: bash

  # clone the repo for the OEF node
  git clone git@github.com:uvue-git/OEFCore.git --recursive && cd OEFCore/

  # build the docker image
  ./oef-core-image/scripts/docker-build-img.sh

  # run the image
  ./oef-core-image/scripts/docker-run.sh -p 3333:3333 -d --

When finished, to stop the image:

.. code-block:: bash

  docker stop $(docker ps | grep oef-core-image | awk '{ print $1 }')

Connect Agents
--------------

With the OEF Node running, we can start to connect agents.

Hello world

.. code-block:: python


  from oef.agents import OEFAgent
  client_agent = OEFAgent("MyFirstAgent", oef_addr="127.0.0.1", oef_port=3333)
  agent.connect()


You can find the sources at `this link <https://github.com/uvue-git/OEFCorePython/tree/develop/examples/echo>`_.

