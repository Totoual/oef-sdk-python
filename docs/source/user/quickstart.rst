.. _quickstart:

Quickstart
==========

This is a quick start guide, for the eager users.

Install
-------

* On Linux Ubuntu:

.. code-block:: bash

  sudo apt-get install protobuf-compiler
  git clone https://github.com/uvue-git/OEFCorePython.git --recursive
  cd OEFCorePython/
  python setup.py install


* On Mac OS X:

.. code-block:: bash

  brew install protobuf
  git clone https://github.com/uvue-git/OEFCorePython.git --recursive
  cd OEFCorePython/
  python setup.py install


* For other platforms and additional details,
  please follow the installation guide: :ref:`install`.


Run a OEF Node
--------------

In a separate terminal:

.. code-block:: bash

  # clone the repo for the OEF node
  git clone git@github.com:uvue-git/OEFCore.git --recursive && cd OEFCore/

  # build the docker image
  ./oef-core-image/scripts/docker-build-img.sh

  # run the image
  ./oef-core-image/scripts/docker-run.sh -p 3333:3333 -d --

When finished, you can stop the image by running the following:

.. code-block:: bash

  docker stop $(docker ps | grep oef-core-image | awk '{ print $1 }')

Connect Agents
--------------

With the OEF Node running, we can start to connect agents.


Write Agents
~~~~~~~~~~~~

The ``GreetingsAgent`` does the following:

* ``on_search_result``: Once the agent receives results from its search,
  the agent sends a ``hello`` message to each agent discovered.
* ``on_message``: whenever the agent receives a ``hello`` message,
  it answers with ine if its greetings.

.. code-block:: python

    >>> a = "a"
    >>> a
    'a'

.. code-block:: python

    from typing import List
    from oef.agents import OEFAgent

    class GreetingsAgent(OEFAgent):

        def on_message(self, origin: str, dialogue_id: int, content: bytes):
            print("[{}]: Received message: origin={}, dialogue_id={}, content={}"
                  .format(self.public_key, origin, dialogue_id, content))
            if content == b"hello":
                print("[{}]: Sending greetings message to {}".format(self.public_key, origin))
                self.send_message(dialogue_id, origin, b"greetings")

        def on_search_result(self, search_id: int, agents: List[str]):
            if len(agents) > 0:
                print("[{}]: Agents found: {}".format(self.public_key, agents))
                for a in agents:
                    self.send_message(0, a, b"hello")
            else:
                print("[{}]: No agent found.".format(self.public_key))


Start Communications
~~~~~~~~~~~~~~~~~~~~

* Instantiate agents:

.. code-block:: python

  client_agent = GreetingsAgent("greetings_client", oef_addr="127.0.0.1", oef_port=3333)
  server_agent = GreetingsAgent("greetings_server", oef_addr="127.0.0.1", oef_port=3333)

* Connect them to the OEF:

.. code-block:: python

  client_agent.connect()
  server_agent.connect()

* The server agent registers itself as a greetings service on the OEF:

.. code-block:: python

  from oef.schema import DataModel, Description
  greetings_model = DataModel("greetings", [], "Greetings service.")
  greetings_description = Description({}, greetings_model)
  server_agent.register_service(greetings_description)

* The client agent executes the search for greetings services:

.. code-block:: python

  from oef.query import Query
  query = Query([], greetings_model)
  client_agent.search_services(query)


When the ``client_agent`` receives a search result from the OEF, the ``on_search_result`` method is executed.

* Execute both agents concurrently

.. code-block:: python

    import asyncio
    loop.run_until_complete(asyncio.gather(
        client_agent.async_run(),
        server_agent.async_run()))

The output should be:

::

    [greetings_client]: Agents found: ['greetings_server']
    [greetings_server]: Received message: origin=greetings_client, dialogue_id=0, content=b'hello'
    [greetings_server]: Sending greetings message to greetings_client
    [greetings_client]: Received message: origin=greetings_server, dialogue_id=0, content=b'greetings'


You can find the full script at
`this link <https://github.com/uvue-git/OEFCorePython/tree/master/examples/greetings/greetings_example.py>`_.

You can also try another version that uses the local implementation of an OEF Node:
`link <https://github.com/uvue-git/OEFCorePython/tree/master/examples/greetings/local_greetings_example.py>`_.

In :ref:`tutorial` you might find all the details and how to implement more complex behaviours.
