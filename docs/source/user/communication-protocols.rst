.. _communication-protocols:

Communication Protocols
========================

OEF Agent can communicate with two categories of entities:

* an OEF Node.
* an OEF Agent (including itself), via an OEF Node.

In this section we will explain all the possible interaction with one of the cited categories of recipients.

Interaction with the OEF Node
------------------------------

An agent can interact with the OEF for the following purposes:

* Establish a connection: `Handshake`
* Register/Unregister as an Agent (in the `Agent Directory`, see :ref:`introduction`)
* Register/Unregister as a Service (in the `Service Directory`, see :ref:`introduction`)
* Search other agents/services

The main difference between the `Agent Directory` and the `Service Directory` is that:

* the former is more general-purpose, whereas the latter is thought to be used by sellers of resources/data.
* in the former one, an agent can register himself with only one description at a time, whereas in the latter
  a service agent can register himself multiple time with different description (and hence discoverable
  in multiple ways).

It is important to notice that most of the mentioned methods are `asynchronous`, which means that the agent does not
waits explicitly for the result of the operations.

Establish a connection: `Handshake`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is the `condition sine qua non` to interact with the OEF Node, and hence with other OEF agents.

.. code-block:: python

    from oef.agents import OEFAgent

    # assuming that an OEF Node is running at localhost on port 3333:
    agent = OEFAgent("agent_identifier", 127.0.0.1", 3333)

    # do the handshake
    agent.connect()

This method is synchronous; that is, the execution of the main thread waits until the connection is done.
The other

In the next sections, we assume that you already have connected the agent to an OEF Node.

Register agent
~~~~~~~~~~~~~~

In order to become discoverable from other agents, an agent can register itself in the `Agent Directory`.

To do so, we use the :func:`~oef.core.OEFCoreInterface.register_agent`:

.. code-block:: python

    from oef.schema import DataModel, AttributeSchema, Description

    # define a data model about "cars"
    car_data_model = DataModel("car", [
        AttributeSchema("manufacturer", str,   True, "The name of the car manufacturer."),
        AttributeSchema("year",         int,   True, "The year of registration."),
        AttributeSchema("luxury",       bool,  True, "Whether the car is a luxury car."),
        AttributeSchema("price",        float, True, "The price of the car."),
    ])

    # define the description of our
    agent_description = Description({
        "manufacturer": "Ferrari",
        "year":         2015,
        "luxury":       True,
        "price":        150000.0
        }, car_data_model)

    # register the agent in the Agent Directory
    agent.register_agent(agent_description)


Unregister agent
~~~~~~~~~~~~~~~~

We can unregister an agent by using the method :func:`~oef.core.OEFCoreInterface.unregister_agent`:

Using the example of before:

.. code-block:: python

    agent.unregister_agent()


Notice that we don't need to use a description, since our agent in the `Agent Directory` is uniquely identified
by the `public key` of the agent.

Register service
~~~~~~~~~~~~~~~~

We can register an agent as a service in the `Service Directory`
by using the method :func:`~oef.core.OEFCoreInterface.register_service`:


.. code-block:: python

    from oef.schema import DataModel, AttributeSchema, Description

    # define a data model about "bookshops"
    bookshop_data_model = DataModel("bookshop", [
        AttributeSchema("name",        str,   True,  "The name of the bookshop."),
        AttributeSchema("city",        str,   True,  "The city where the bookshop is located."),
        AttributeSchema("address",     str,   True,  "The address where the bookshop is located."),
        AttributeSchema("online",      bool,  False, "Whether it provides online catalog and purchases."),
        AttributeSchema("second_hand", bool,  False, "Whether it is a second hand bookshop."),
    ])

    # define a description, that is an instance of the data model
    service_description = Description({
        "name":         "John Smith's Bookshop",
        "city":         "Cambridge",
        "address":      "Helmore Building, Anglia Ruskin University, Cambridge Campus",
        "second_hand":  False

    }, bookshop_data_model)


    agent.register_service(service_description)

Notice: nothing prevent us to register `the same agent` (with the same public key) in the Agent Directory,
or as another type of service in the `Service Directory`.

Unregister service
~~~~~~~~~~~~~~~~~~

We can unregister a service with a given description from the `Service Directory`
by using the method :func:`~oef.core.OEFCoreInterface.unregister_service`:

Continuing with the bookshop example:

.. code-block:: python

    agent.unregister_service(service_description)


Notice that, differently from the :func:`~oef.core.OEFCoreInterface.unregister_agent` described before, we need to
provide the description that we used when registered, because we might have registered our service
with multiple descriptions.


Search agents
~~~~~~~~~~~~~

In order to find other agents, we have to query the OEF Node about the kind of agents we are interested in.

To do so, we can use the API provided by the :mod:`~oef.query` module and building :class:`~oef.query.Query` object
as explained in :ref:`query-language`

Once our query is ready, we can use the :func:`~oef.core.OEFCoreInterface.search_agents` method.

Suppose we want to search cars whose manufacturer is ``Ferrari``. Continuing with the definition of the data model
`in this section <#register-agent>`__

.. code-block:: python

    from oef.query import Query, Constraint, Eq

    # specify a query to be evaluated by the OEF Node
    # on the Agent Directory descriptions.
    ferrari_query = Query([
        Constraint("manufacturer", Eq("Ferrari"))
    ], car_data_model)

    # specify a search id. This id will be used by the
    # OEF Node to refer to the right search request when
    # it will send back the result.
    search_id = 0
    agent.search_agents(0, ferrari_query)

    agent.run()


The ``search_agents`` function will send the search message to the OEF Node, which eventually will answer with a
*list of the public keys* of agents satisfying the query.

In this specific case, the OEF Node will return a list of the public keys of all the OEF agents that:

- are successfully registered in the `Agent Directory`;
- are registered with the ``car_data_model``;
- their manufacturer is ``Ferrari``.

The :func:`~oef.agents.Agent.run` is mandatory to receive the search result. Indeed, the main loop of the agent
will automatically call the :func:`~oef.agents.Agent.on_search_result` method implemented by the class, as soon as the
search result message has been received.

Hence, to specify a behaviour when a search result is called, you need to:

- extend the class :class:`~oef.agents.OEFAgent`
- override the :func:`~oef.agents.Agent.on_search_result` method.

The following sequence diagram depicts the sequence of messages exchanged between the OEF Node and the agent that
sent the search request.

.. mermaid:: ../diagrams/search_agents.mmd


Search services
~~~~~~~~~~~~~~~

The :func:`~oef.core.OEFCoreInterface.search_services` method is the analogous counterpart of the
:func:`~oef.core.OEFCoreInterface.search_agents`, but used to discover services in the `Service Directory`.

Suppose we want to search bookshop located in ``Cambridge``. Continuing with the definition of the data model
`in this section <#register-service>`__

.. code-block:: python

    from oef.query import Query, Constraint, Eq

    # specify a query to be evaluated by the OEF Node
    # on the Service Directory descriptions.
    cambridge_query = Query([
        Constraint("city", Eq("Cambridge"))
    ], bookshop_data_model)

    # specify a search id. This id will be used by the
    # OEF Node to refer to the right search request when
    # it will send back the result.
    search_id = 0
    agent.search_services(0, cambridge_query)

    agent.run()


The ``search_services`` function will send the search message to the OEF Node, which eventually will answer with a
*list of the public keys* of services satisfying the query.

In this specific case, the OEF Node will return a list of the public keys of all the OEF service agents that:

- are successfully registered in the `Service Directory`;
- are registered with the ``bookshop_data_model``;
- their "city" field has value ``Cambridge``.

The :func:`~oef.agents.Agent.run` is mandatory to receive the search result. Indeed, the main loop of the agent
will automatically call the :func:`~oef.agents.Agent.on_search_result` method implemented by the class, as soon as the
search result message has been received.

Hence, to specify a behaviour when a search result is called, you need to:

- extend the class :class:`~oef.agents.OEFAgent`
- override the :func:`~oef.agents.Agent.on_search_result` method.

The following sequence diagram depicts the sequence of messages exchanged between the OEF Node and the agent that
sent the search request.

.. mermaid:: ../diagrams/search_services.mmd




Interaction with other OEF Agents
---------------------------------


