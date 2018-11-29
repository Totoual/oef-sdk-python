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

`Here <https://github.com/uvue-git/OEFCorePython/tree/master/examples/echo>`_
you can find the full code of the examples.

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
          """ this method is called whenever a new message is sent to this agent.
          We send the received message back to the origin"""

          print("Received message: origin={}, conversation_id={}, content={}".format(origin, conversation_id, content))
          print("Sending {} back to {}".format(content, origin))
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
  server_agent = EchoServiceAgent("echo_server", oef_addr="127.0.0.1", oef_port=3333)
  server_agent.connect()

Define a Data Model and a Description
``````````````````````````````````````

In order to make our agent discoverable from other agents, we need to define a `description` (instance of a schema),
which refers to a `data model` (abstract definition of the schema).
In this way, other agents can find our service by making `queries` (defined over the same data model) to the OEF.

.. code-block:: python

  from oef.schema import DataModel, Description
  echo_model = DataModel("echo", [], "echo data service.")
  echo_description = Description({}, echo_model)


Our data model ``echo_model`` is very straightforward.
It has an empty list of `attribute schema`, just for make the example simpler.

The ``echo_description``, that is the instantiation of our abstract data model ``echo``, is defined accordingly.

Register the service
````````````````````

Now that we have a description for our service, let's register our service agent to the OEF:

.. code-block:: python

  server_agent.register_service(echo_description)


This instruction will notify the OEF Node that there is a new service available.

When another agent will make a query on the ``echo_model``, if ``echo_description`` satisfies the constraint of that
query, our agent will be one of the result of that query.


Run the agent
`````````````
To run the agent waiting for events:

::

  server_agent.run()


The ``run()`` method is blocking, so you have to switch to another terminal/console to launch the client.

For some particular use cases, you may want to use the associated ``async`` method, that is ``async_run()``.


Echo Agent client
~~~~~~~~~~~~~~~~~

The `EchoClientAgent` implements our `echo client`, that is the consumer of the service we implemented in the previous
section.

.. code-block:: python

  import uuid
  from typing import List

  from oef.agents import OEFAgent

  class EchoClientAgent(OEFAgent):

      def on_message(self, origin: str, conversation_id: str, content: bytes):
          print("Received message: origin={}, conversation_id={}, content={}".format(origin, conversation_id, content))

      def on_search_result(self, agents: List[str]):
          if len(agents) > 0:
              print("Agents found: ", agents)
              msg = b"hello"
              for agent in agents:
                  print("Sending {} to {}".format(msg, agent))
                  self.send_message(str(uuid.uuid4()), agent, msg)
          else:
              print("No agent found.")


The ``on_message`` method has the same semantics of the one implemented in the ``EchoServiceAgent`` class. In this case,
we don't implement any complex behavior (we just print the received message).

The ``on_search_result`` callback is called whenever the agent receives a search result followed by a search query with
``search_agents()`` or ``search_services()`` methods.

In our case, the agent just sends a ``"hello"`` message (in bytes) to every discovered service,
by using the ``send_message()`` method.

Connect to the OEF
``````````````````

Analogously to the previous section, we connect our client to the OEF.

.. code-block:: python

  client_agent = EchoClientAgent("echo_client", oef_addr="127.0.0.1", oef_port=3333)
  client_agent.connect()


Make a query
````````````

Now we need to search for agents who provides the ``echo` service.

To do so, we create a ``Query`` referring to the ``echo`` data model. The first parameter is a list
of *constraints* over the attributes of the data model. However, since our data model is trivial,
our query just returns all the agents that are registered with the `echo` data model.

.. code-block:: python

  # create a query for the echo data model
  from oef.schema import DataModel
  from oef.query import Query
  echo_model = DataModel("echo", [], "Echo data service.")
  echo_query = Query([], echo_model)


Search for services
```````````````````

Once we have a query, we can ask the OEF to returns all service agents that satisfy those constraints.

.. code-block:: python

  client_agent.search_services(echo_query)

Wait for search results
```````````````````````

The client agent needs to wait for the search result from the OEF Node:

.. code-block:: python

  # wait for events
  client_agent.run()


Once the OEF Node computed the result, the ``on_search_result`` callback is called.


Message Exchange
~~~~~~~~~~~~~~~~


If you run the agents in different consoles, you can check the log messages that they produced.

The output from the client agent should be:

::

  Agents found:  ['echo_server']
  Sending b'hello' to echo_server
  Received message: origin=echo_server, conversation_id=573a6643-22c3-4a88-aede-77bf65859c5f, content=b'hello'

Whereas, the one from the server agent is:

::

  Received message: origin=echo_client, conversation_id=573a6643-22c3-4a88-aede-77bf65859c5f, content=b'hello'
  Sending b'hello' back to echo_client


The order of the exchanged message is the following:

- The server notify the OEF Node that it is able to serve other agents;
- The ``echo_client`` make a query to the OEF Node;
- The OEF Node sends back the list of agents who satisfy the condition in the query (the only agent is ``echo_server``);
- The client sends ``"hello"`` message to the OEF Node, destined to the ``echo_server``;
- The OEF Node dispatch the message from ``echo_client`` to ``echo_server``;
- The ``echo_server`` receives the message and sends back a new message, destined to ``echo_client``, to the OEF Node;
- The OEF Node dispatch the message from ``echo_server`` to ``echo_client``;
- The ``echo_client`` receives the echo message.


Second example: Weather Station
-------------------------------

In this second example, consider the following scenario:

* A `weather station` that provides measurements of some physical quantity (e.g. wind speed, temperature, air pressure)
* A `weather client` interested in these measurements.

However, the owner fo the weather station wants to sell the data it measure. In the next sections, we describe a
protocol that allow the agents to:

* request for resources (physical assets, services, informations etc.)
* make price proposals on the negotiated resources
* accept/decline proposals.


You can check the code `here <https://github.com/uvue-git/OEFCorePython/tree/master/examples/weather>`_.

Weather Station Agent
~~~~~~~~~~~~~~~~~~~~~




Weather Client Agent
~~~~~~~~~~~~~~~~~~~~~


