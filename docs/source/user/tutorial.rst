.. _tutorial:

First OEF Agents
================

In this guide, we show you some examples of how to develop and run OEF agents.


Initialization
--------------


Setup a OEF Node
~~~~~~~~~~~~~~~~

To be able to follow the following examples, we need to set up an OEF Node. It will manage the discovery of agents
and the communications between agents.

Using Docker
````````````

You can use a Docker image provided by the `OEFCore <https://github.com/uvue-git/OEFCore.git>`_,
by following these steps:

* Clone OEFCore

.. code-block:: bash

  git clone git@github.com:uvue-git/OEFCore.git --recursive && cd OEFCore/

* Build the image

.. code-block:: bash

  ./oef-core-image/scripts/docker-build-img.sh

* Run the image. This will start the OEF node, listening to port ``3333`` at ``localhost``:

.. code-block:: bash

  ./oef-core-image/scripts/docker-run.sh -p 3333:3333 --

This will busy your current terminal. If you want to run the OEF node in background, add the ``-d`` flag:

.. code-block:: bash

  ./oef-core-image/scripts/docker-run.sh -p 3333:3333 -d --

Once done with the tutorial, you can stop the container as follows

.. code-block:: bash

  docker stop $(docker ps | grep oef-core-image | awk '{ print $1 }')

Compiling from source
`````````````````````

You will need:

* ``cmake``
* ``gcc``
* Google Protocol Buffers library.

On Linux (Ubuntu) you can run:

::

  git clone https://github.com/uvue-git/OEFCore.git --recursive && cd OEFCore
  sudo apt-get install cmake protobuf-compiler libprotobuf-dev
  mkdir build && cd build
  cmake ..
  make -j 4

And to run a OEFNode:

::

  ./apps/node/Node


For full details, please follow the
`installation instructions for the OEFCore <https://github.com/uvue-git/OEFCore/blob/master/INSTALL.txt>`_.


Optional: set up the logger
~~~~~~~~~~~~~~~~~~~~~~~~~~~

It might be useful to see logging messages to better understand what happens behind the scenes.

To do so, run the following instructions at the beginning of your scripts:

.. code-block:: python

  import logging
  from oef.logger import set_logger
  set_logger("oef", logging.DEBUG)



First example: Echo agent
---------------------------

In this section we will develop an `echo agent`. That is, whenever it receives a message from another agent, it replies
with the same message.

First, we define the service agent that implements the echo service.
Then, we implement other client agents to interact with the echo service.

Echo Agent service
~~~~~~~~~~~~~~~~~~

Let's start to implement the echo service agent. To do so, we define a new class, ``EchoServiceAgent``, that extends
``OEFAgent`` class and redefine the behaviour of the ``on_message`` method.

The ``on_message`` method of an agent is called whenever a simple message is destined to him.
In this case, we just send the message back to the source of the message, through the OEF.

In later examples we will see more complex protocol and how to implement the associated callbacks.

.. code-block:: python

  from oef.agents import OEFAgent

  class EchoServiceAgent(OEFAgent):

      def on_message(self, origin: str, conversation_id: str, content: bytes):
          # this method is called whenever a new message is sent to this agent.
          # we just send the received message back to the origin.
          self.send_message(conversation_id, origin, content)


Connect to the OEF
``````````````````

In order to connect a (service) agent to the OEF, we need to specify:

* A unique identifier for the agent;
* The IP address and port of the OEF Node on which we want to register;

As identifier we will use ``echo_server``. As IP address and port pair, choose the one according to your OEFNode
instance running. If you followed the previous instructions, they should be ``127.0.0.1`` and ``3333`` respectively.

.. code-block:: python

  # create agent and connect it to OEF
  agent = EchoServiceAgent("echo_server", oef_addr="127.0.0.1", oef_port=3333)
  agent.connect()

Define a Data Model and a Description
``````````````````````````````````````

In order to make our agent discoverable from other agents, we need to define a `description` (instance of a schema),
which refers to a `data model` (abstract definition of the schema).
In this way, other agents can find our service by making `queries` (defined over the same data model) to the OEF.

.. code-block:: python

  echo_model = DataModel("echo", [], "echo data service.")
  echo_description = Description({}, echo_model)


Our data model ``echo_model`` is very straightforward.
It has an empty list of `attribute schema`, just for make the example simpler.

The ``echo_description``, that is the instantiation of our abstract data model ``echo``, is defined accordingly.

Register the service
````````````````````

Now that we have a description for our service, let's register our service agent to the OEF:

.. code-block:: python


  agent.register_service(echo_description)


This instruction will notify the OEF Node that there is a new service available.

When another agent will make a query on the ``echo_model``, if ``echo_description`` satisfies the constraint of that
query, our agent will be one of the result of that query.


Run the agent
`````````````
To run the agent waiting for events:

::

  agent.run()


For some particular use cases, you may want to use the associated ``async`` method, that is ``async_run()``.


Echo Agent client
~~~~~~~~~~~~~~~~~

TODO
