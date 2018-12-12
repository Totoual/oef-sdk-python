.. _introduction:

Introduction
============

What is Fetch
-------------

**Fetch promotes a world** where digital entities can exist, interact, and collaborate/cooperate by exchanging
data services *autonomously* on behalf of their representatives.
These digital entities are software agents augmented by machine
learning and AI capabilities and known as  *Autonomous Economic Agents* (AEAs).
Fetch enables a *data marketplace* where AEAs can be attached
to data sources (such as IoT devices) to propose a data service as a *Data Service Provider*,
and AEAs looking for data can get it as a *Data Service Consumer*. AEAs will register,
query, and negotiate data services on behalf of their representatives.

.. image:: https://github.com/uvue-git/OEFCorePython/wiki/imgs/fetch-world.png
   :target: https://github.com/uvue-git/OEFCorePython/wiki/imgs/fetch-world.png
   :alt: Fetch World

The *Fetch network* achieves this by providing a 3-level layered software architecture:
*Smart Ledger*, *Open Economic Framework* (OEF), and *Autonomous Economic Agent* (AEA) layer.
The bottom layer is the Ledger. It implements scalable transactions between agents
allowing for data service contracts and basic trust mechanism. The OEF layer implements agent and data exploration.
Finally, the AEA layer implements data models and communication protocols for agents
to interact with the OEF and with each other.

What is OEF? (Open Economic Framework)
--------------------------------------

Overview
~~~~~~~~

**To access Fetch world**, AEAs (or just agents from now on) need to connect to a Fetch node that deploys the OEF.

The OEF-core is the part of the OEF that manages primitive operations:
agent connections, registrations, search, and queries.
It implements the core concepts and protocols needed to allow agents
to live, interact and advance in the Fetch world.
It is also the interface to the ledger.

The OEF-core keeps track of connected agents in an *AgentDirectory* and registered data services
in a *ServiceDirectory*.

For each connected and correctly identified agent, the AgentDirectory stores its ID,
description (as a property list), and session. If the agent register a data service,
the data service along with the agent ID will be stored in the ServiceDirectory.

.. image:: https://github.com/uvue-git/OEFCorePython/wiki/imgs/oef-core.png
   :target: https://github.com/uvue-git/OEFCorePython/wiki/imgs/oef-core.png
   :alt: OEF-core


Agent life-cycle
~~~~~~~~~~~~~~~~

A typical agent life-cycle on the OEF consists of:

1. Connect to the OEF-core
2. Register a DataService, query for a DataService, or search for agents
3. Interact with other agents
4. Unregister DataServices, if any
5. Disconnect from the OEF-core

Agent-to-OEF core interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**1.** To be part of the Fetch world, an agent first needs to connect to a Fetch node on the OEF-Core
 and identify itself using its public key.


.. image:: https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-connect-2.png
   :target: https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-connect-2.png
   :alt: Connect Operation

**2.** Once connected and correctly identified, a *session* is created on the OEF-Core side.
This *session* object will be used to directly communicate with the OEF-core as well as
with other agents.

Once a session is in place, an agent can:
- Register a DataService: propose a DataService by registering a data model (a description) and wait for interested agents to contact it. Note that the actual data is not sent

.. image:: https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-register.png
   :target: https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-register.png
   :alt: Register Operation

- Query for a DataService: query the OEF-core for a data model with a set of constraints

.. image:: https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-query.png
   :target: https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-query.png
   :alt: Query Operation

- Search for agents: conduct an agent property-based search (GPS position, market type, ...)

.. image:: https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-search.png
   :target: https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-search.png
   :alt: Search Operation


Agent-to-agent interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

An agent spends nearly its entire life-time in the Fetch world
interacting with other agents. An interaction is initiated by either contacting
an agent (using the ID received from a query or a search) or receiving a message
from one (in response to a registered data service or based on registered property list).
The previous operations thus served as preliminary steps in agent-to-agent interactions
by providing a mechanism for discovery.

Interactions between agents are implemented using *Conversation* objects.
A Conversation object maintains a communication channel between a pair or a group of agents through their Sessions.
A pair of agents can have multiple Conversation objects (i.e. parallel communication channels).

.. image:: https://github.com/uvue-git/OEFCorePython/wiki/imgs/oef-conversation.png
   :target: https://github.com/uvue-git/OEFCorePython/wiki/imgs/oef-conversation.png
   :alt: Conversations

A Conversation object is created on-the-fly the first time a message is received
with a new conversation ID. The first time an agent wants to contact another agent
it has to create a new conversation object to that agent.
Once a conversation is created, the agent can use it to send and receive message
directly to/from the participating agents.
A newly created agent Session can be seen as a Session with an implicit Conversation object
to the OEF-core.

*Note: In the current implementation of the OEF-core, Conversation objects really exist only on
the agents side. On the OEF-core side, they exist only conceptually.*

Agent-to-agent data and communication protocol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once a conversation has been established, particpating agents can use it to exchange messages.
Messages must be objects of types ``InMessage`` or ``OutMessage``.

.. code-block:: proto

  message Agent {
      message InMessage {
          required string cid = 1; // conversation ID
          required string origin = 2;
          required bytes content = 3;
      }

      message OutMessage {
          required string cid = 1; // conversation ID
          required string destination = 2;
          required bytes content = 3;
      }
  }


The ``content`` field is where the actual message content is stored
and from where it will be accessed when received by the other participant in the conversation.

Agents are free to negotiate and agree upon a communication protocol
and message content representation at the start of a conversation.
Nonetheless, Fetch Agent layer offers a default for both, available for agents to use at will.

Regarding message content representation, there is a default ``Data`` type
that can be serialized to ``bytes`` and stored in the ``content`` field
of an ``OutMessage``, and respectively on the other side can be read
from the ``content`` field of an ``InMessage`` and deserialized to a ``Data`` object.

.. code-block:: proto

  message Data {
      required string name = 1;
      required string type = 2; // should be enum
      repeated string values = 3;
  }


For agent communication protocol, it offers FIPA interaction protocol messages.

.. code-block:: proto

  import "query.proto";

  message Fipa {
      message Cfp {
          optional Query.Model query = 1;
          extensions 2 to 100;
      }
      message Propose {
          repeated Query.Instance objects = 1;
          extensions 2 to 100;
      }
      message Accept {
          repeated Query.Instance objects = 1;
          extensions 2 to 100;
      }
      message Close {
      }
      message Message {
          required int32 msg_id = 1;
          required int32 target = 2;
          oneof msg {
              Cfp cfp = 3;
              Propose propose = 4;
              Accept accept = 5;
              Close close = 6;
          }
      }
  }
