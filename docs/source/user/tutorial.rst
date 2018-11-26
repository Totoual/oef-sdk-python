.. _tutorial:

Tutorial
========

Initialization
--------------


Setup a OEF Node
~~~~~~~~~~~~~~~~

To be able to follow the following examples, we need to set up an OEF Node. It will manage the discovery of agents
and the communications between agents.

To do so, follow these steps:

* Clone OEFCore

.. code-block:: bash

  git clone git@github.com:uvue-git/OEFCore.git --recursive && cd OEFCore/

* Build the image

.. code-block:: bash

  ./oef-core-image/scripts/docker-build-img.sh

* Run the image. This will start the OEF node

.. code-block:: bash

  ./oef-core-image/scripts/docker-run.sh -p 3333:3333 --

This will busy your current terminal. If you want to run the OEF node in background, add the ``-d`` flag:

.. code-block:: bash

  ./oef-core-image/scripts/docker-run.sh -p 3333:3333 -d --

Once done with the tutorial, you can stop the container as follows

.. code-block:: bash

  docker stop $(docker ps | grep oef-core-image | awk '{ print $1 }')


Optional: set up the logger
~~~~~~~~~~~~~~~~~~~~~~~~~~~

It might be useful to see logging messages to better understand what happens behind the scenes.

To do so, run the following instructions at the beginning of your scripts:

.. code-block:: python

  import logging
  from oef.logger import set_logger
  set_logger("oef", logging.DEBUG)


