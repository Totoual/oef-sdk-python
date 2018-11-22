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


## Tutorial 

**Fetch promotes a world** where digital entities can exist, interact, and collaborate/cooperate by exchanging
data services *autonomousely* on behalf of their representatives.
These digital entites are software agents augumented by machine
learning & AI capabilities and known as  *Autonomous Economic Agents* (AEAs).
Fetch enables a *data marketplace* where AEAs can be attached
to data sources (such as IoT devices) to propose a data service as a *Data Service Provider*,
and AEAs looking for data can get it as a *Data Servicer Consumer*. AEAs will register,
query, and negociate data services on behalf of their representatives.

The *Fetch network* achieves this by providing a 3-level layered software architecture: 
*Ledger*, *Open Economic Framework* (OEF), and *Agent* layer. 
The buttom layer is the Ledger. It implements scalable transactions between agents
allowing for data service contracts and basic trust mechanism. The OEF layer implements agent & data exploration. 
Finally, the Agent layer implements data models and communication protocols for agents 
to interact with the OEF and with each other.


![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/fetch-world.png "Fetch World")

[//]: # (source https://whiteboardfox.com/161913-1374-1406 )


**The goal of this tutorial** is to help you build agents for Fetch
using the beta version of the OEF (named *OEF-core*) and the early-beta version of
the OEF-core python agent SDK. It is three parts. First part introduces key concepts 
of the OEF-core to keep in mind when developing agents. Second part is a step-by-step hands-on
tutorial to build weather agents using Python SDK. Last part is optional and targets mainly SDK developers. It provides a
deeper view of the OEF-core implementation and communication protocols.

***Contents***

1. [Introduction to OEF-core](https://github.com/uvue-git/OEFCorePython/blob/alt/README.md#1-open-economic-framework-oef-core)
    - [Overview](https://github.com/uvue-git/OEFCorePython/tree/alt#overview) 
    - [Agent life-cycle](https://github.com/uvue-git/OEFCorePython/tree/alt#agent-life-cycle) 
    - [Agent-to-OEF core interactions](https://github.com/uvue-git/OEFCorePython/tree/alt#agent-to-oef-core-interactions) 
    - [Agent-to-agent interactions](https://github.com/uvue-git/OEFCorePython/tree/alt#agent-to-agent-interactions) 
    - [Agent-to-agent data representation & communication protocol](https://github.com/uvue-git/OEFCorePython/tree/alt#agent-to-agent-data--communication-protocol)
2. [Hands-on: step-by-step agents development tutorial](https://github.com/uvue-git/OEFCorePython/tree/alt#2-agent-development-oef-core-python-sdk)
    - [Environment setup](https://github.com/uvue-git/OEFCorePython/tree/alt#environment-setup)
    - [Examples: echo agents, weather agents](https://github.com/uvue-git/OEFCorePython/tree/alt#hands-on)
    - [Error Management](https://github.com/uvue-git/OEFCorePython/tree/alt#error-management)
3. [OEF-core for SDK developers](https://github.com/uvue-git/OEFCorePython/tree/alt#3-oef-core--agent-layer-for-sdk-developers)
    - [Low-level communication protocol](https://github.com/uvue-git/OEFCorePython/tree/alt#oef-core-low-level-communication-protocol)
    - [Data serialization protocol](https://github.com/uvue-git/OEFCorePython/tree/alt#oef-core-data-serialization-protocol)
    - [Operations](https://github.com/uvue-git/OEFCorePython/tree/alt#oef-core-operations)
    - [Conversation operations](https://github.com/uvue-git/OEFCorePython/tree/alt#conversation-operations)
    - [Agent layer internals](https://github.com/uvue-git/OEFCorePython/tree/alt#agent-layer-internals)




## 1. Open Economic Framework (OEF-core)
#### Overview
**To access Fetch world**, AEAs (or just agents from now on) need to connect to a Fetch node that deploys the OEF.
The OEF-core is the part of the OEF that manages primitive operations:
agents connections, registrations, search, and queries. 
It implements the core concepts and protocols needed to allow agents
to live, interact and advance in the Fetch world.
It is also the interface to the ledger.

The OEF-core keeps track of connected agents in an *AgentDirectory* and registred data services 
in a *ServiceDirectory*.
For each connected and correctly identified agent, the AgentDirectory stores its ID, 
description (as a property list), and session. If the agent register a data service, 
the data service along with the agent ID will be stored in the ServiceDirectory.

![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/oef-core.png "OEF-Core")

[//]: # (source https://whiteboardfox.com/156910-5382-1125 )

#### Agent life-cycle 
A typical agent life on the Fetch world consists in:
1. Connect to the OEF-core
2. Register a DataService, query for a DataService, or search for agents
3. Interact with other agents
4. Unregister DataServices, if any
5. Disconnect from the OEF-core

#### Agent-to-OEF core interactions

**1.** To be able to be part of the Fetch world, an agent needs to connect and identify
itself (using its public key) first to a Fetch node through the OEF-Core. 

<img src="https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-connect-2.png" 
    alt="Connect Operation" />

[//]: # (source https://whiteboardfox.com/159206-3102-6954 )

**2.** Once connected and correctely identified, a *session* is created on the OEF-Core side. 
This *session* object will be used to directly communicate with the OEF-core as well as
with other agents.
Once connected and correctely identified, an agent can:
- Register a DataService: propose a DataService by registering a data model (a description) and wait for interested agents to contact it. Note that the actual data is not sent

<img src="https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-register.png" 
    alt="Register Operation"/>

[//]: # (source https://whiteboardfox.com/159218-9876-7946 )

- Query for a DataService: query the OEF-core for a data model with a set of constraints

<img src="https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-query.png" 
    alt="Query Operation"/>

[//]: # (source https://whiteboardfox.com/159221-1849-4958 )

- Search for agents: conduct an agent property-based search (GPS position, market type, ...)

<img src="https://github.com/uvue-git/OEFCorePython/wiki/imgs/operation-search.png" 
    alt="Search Operation" />

[//]: # (source https://whiteboardfox.com/159232-2027-9742 )

*Note: Not implemented yet*


#### Agent-to-agent interactions

An agent spend almost all of its life time in the Fetch world 
interacting with other agents. An interaction is intiated by either contacting
an agent (using the ID received from a query or a search) or receiving a message
from one (in answer to a registred data service or based on registred property list).
In that sense, the previous operations were only preliminaries for agents interactions by providing discovery.


Interactions between agents are implemented using *Conversation* objects.
A Conversation object maintains a communication channel between a pair or a group of agents through their Sessions. 
A pair of agents can have multiple Conversation objects (i.e. parallel communication channels).


![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/oef-conversation.png "Conversations")

[//]: # (source https://whiteboardfox.com/162659-6953-5058 )

A Conversation object is created on-the-fly the first time a message is received 
with a new conversation ID. The first time an agent want to contact another agent 
it have to create a new conversation object to that agent.
Once a conversation is created, the agent can use it to send and receive message 
directly to/from the participating agents. 
A newly created agent Session can be seen as a Session with an implicit Conversation object
to the OEF-core.

*Note: In the current implementation of the OEF-core, Conversation objects really exist only on 
the agents side. On the OEF-core side, they exist only conceptually.*

#### Agent-to-agent data & communication protocol

Once a conversation has been established, particpating agents can use it to exchange messages.
Messages must be objects of types `InMessage` or `OutMessage`.

```proto
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
```

The `content` field is where the actual message content is stored 
and from where it will be accecced when received on the other end.
The message content representation and communication protocol are completely 
free to negociate and agree upon by participating agents, 
at the start of the conversation for example. 
Nonetheless, Fetch Agent layer offers a default for both, available for agents to use at will.

For message content representation, it offers a `Data` type that can be serialized
to `bytes` and stored in the `content` field of an `OutMessage`, and repectively on the other side can be read
from the `content` field of an `InMessage` and deserialized to a `Data` object.

```proto
message Data {
    required string name = 1;
    required string type = 2; // should be enum
    repeated string values = 3;
}

```

For agent communication protocol, it offers FIPA interaction protocol messages.

```proto
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
```

*Note: FIPA is not implemented yet*








## 2. Agent development (OEF-core Python SDK)

### Environment setup
To be able to follow the hands-on section, we need to setup a working OEF node and install python SDK.
1. Clone OEFCorePython and checkout the `alt` branch
```bash
$ git clone git@github.com:uvue-git/OEFCorePython.git && cd OEFCorePython/ 
$ git checkout alt
```
2. Build docker image
```bash
$ docker build -t oef_tutorial -f oef_tutorial_dkr/Dockerfile .
```
3. Run the image. This will start the OEF node
```bash
$ docker run oef_tutorial
```
Once done with the tutorial, you can stop the container as follows
```bash
$ docker stop $(docker ps | grep oef_tutorial | awk '{ print $1 }')
```
### Hands-on 
Now that the environment has been setup and an OEF node is running, Let's write some code.
First, connect to the docker container running the OEF node.
```bash
# open a new terminal
$ docker exec -it $(docker ps | grep oef_tutorial | awk '{ print $1 }')  bash
root@97689a36f6c9:~/dev/OEFCorePython/examples# python3 
```
```python
import oef
from oef import Agent
agent = Agent("basic_agent", "127.0.0.1")
aget.connect()
```
output
```bash
[OEF-Agent][INFO] Successfully connected to OEF.
True
```
Congratulations! you just wrote your first agent.
As it's id suggests, it is a very basic agent. It doesn't do anything 
and if contacted by other agents it will close the conversation.
To exit agent execute:
```python
Agent.exit()
```
#### Echo agents
Let's write more interesting agents, agents that actually interact with each other.
We start simply by writing echo agents: a server and a client. `echo_server` will be 
the data service provider and `echo_client` will be the data service consumer.

##### Echo server
```python
# echo_server
import oef
from oef import Agent, DataModel, AttributeSchema, Description, ConversationAscii
agent = Agent("echo_server", "127.0.0.1")
agent.connect()

# register a data service on the OEF
echo_model = DataModel("echo", [AttributeSchema("echo_ascii", bool, True)], "echo data service.")
echo_description = Description({"echo_ascii": 1}, echo_model)

agent.register_service(echo_description)

```
output
```
[OEF-Agent][INFO] Successfully connected to OEF.
True
[OEF-Agent][INFO] Successfully registred DataService.
True
```
To register `echo_description` as a service, the `echo_server` uses method `register_service(desc : Description)`.

Note that at this stage, the `echo_server` agent is still not completely setup
as it will not answer other agents messages. To do so, we need to
(1) register a callback function to handle new conversations
(2) run the agent.

Lets first write the callback function.
```python
# echo service
async def handle_echo_requests(client,agent):
  print("[echo server] new conversation %s from %s" % (client.id, client.correspondant))
  conv = ConversationAscii(client)
  # get message
  message = await conv.areceive()
  print("[echo server] received message: %s" % message)
  echoed_message = message + "_echoed"
  # send message back
  await conv.asend(echoed_message)
  print("[echo server] message sent back %s to %s" % (echoed_message,conv.correspondant))
  print("[echo server] message sent back %s to %s" % (echoed_message,conv.correspondant))
```
Then register it.
```python
# setup a callback for new conversations
agent.on_new_conversation(handle_echo_requests)
```
output
```bash
[OEF-Agent][INFO] Function <function handle_echo_requests at 0x7f76083d22f0> registred as callback for new conversations
```
The agent method `on_new_conversation(callback_func(con: Conversation, agent: Agent))`
is used to register the callback function.
It expect a function with two arguments: `conv` representing the newely created conversation object, and
`agent` representing the targeted agent.

Finally, start the agent.
```python
agent.run()
```
output
```bash
[OEF-Agent][INFO] Waiting for conversations ...
```
##### Echo client
Repectively, `echo_client` agent will have to query the OEF for `echo` service, send a message
to the agent providing the service and wait for it to be echoed.
```bash
# open a new terminal
$ docker exec -it $(docker ps | grep oef_tutorial | awk '{ print $1 }')  bash
root@97689a36f6c9:~/dev/OEFCorePython/examples# python3
```
```python
# echo_client
import  oef
from oef import Agent, DataModel, AttributeSchema, Query, Constraint, Eq, ConversationAscii
agent = Agent("echo_client", "127.0.0.1")
agent.connect()

# query OEF for DataService providers
echo_model = DataModel("echo", [AttributeSchema("echo_ascii", bool, True)], "echo data service.")
echo_query = Query([Constraint(AttributeSchema("echo_ascii", bool, True), Eq(True))], echo_model)
echo_servers = agent.search_services(echo_query)
```
output
```bash
[OEF-Agent][INFO] Successfully connected to OEF.                                                                                   
True   
[OEF-Agent][INFO] search_services answer : ['echo_server'] 
```
To initiate conversation with `echo_servers[0]` and interact with it, the API offers two possible way to do it:
synchronous and asynchrnous.
```python
# echo_client sync
# create a conversation 
conv = ConversationAscii(agent.new_conversation(echo_servers[0],echo_servers[0]))

message = "Hi there!"
conv.send(message)
print("[echo client] message %s sent to %s" % (message,conv.correspondant))

echoed_message = conv.receive()
print("[echo client] received message %s from %s" % (echoed_message,conv.correspondant))

Agent.exit()
```
output
```bash
True
[echo client] message Hi there! sent to echo_server
[echo client] received message Hi there!_echoed from echo_server
```
In the asynchronous version, `echo_client` needs to pass a function to the method `run(func(agent: Agent))`
to execute when `run` will be called.
```python
# echo client async
async def say_hi(agent):
  # create a conversation with the first echo server
  conv = ConversationAscii(agent.new_conversation(echo_servers[0],echo_servers[0]))
  
  message = "Hi there!"
  await conv.asend(message)
  print("[echo client] message %s sent to %s" % (message,conv.correspondant))
  
  echoed_message = await conv.areceive()
  print("[echo client] received message %s from %s" % (echoed_message,conv.correspondant))


# run agent
agent.run(say_hi)

# run will exit agent when say_hi returns
```
output
```
[OEF-Agent][INFO] Running agent ...
[echo client] message Hi there! sent to echo_server
[echo client] received message Hi there!_echoed from echo_server
```
#### Weather agents
At this stage, we have covered pretty much all a python agent developer needs to know
to write fully-featured Fetch agents.
More practical examples are weather agents.
##### meteostation and meteoclient
Check folder `examples/weather` for examples of a weather station and a weather client agents.
```bash
# in a new terminal
$ docker exec -it $(docker ps | grep oef_tutorial | awk '{ print $1 }')  bash
root@97689a36f6c9:~/dev/OEFCorePython/examples# python3 weather/meteostation_async.py MeteoSt 

# in a new terminal
$ docker exec -it $(docker ps | grep oef_tutorial | awk '{ print $1 }')  bash
root@97689a36f6c9:~/dev/OEFCorePython/examples# python3 weather/meteoclient_sync.py
```
##### meteo broker
Folder `examples/weather_broker` provides a more elaborate agent. 
`meteobroker` agent register a `broker` service with `weather_data` as attribute. 
`meteobroker_client_sync` queries the OEF for `weather_data`
brokers and buy from the first one, if the price is less than certain amount.
When contacted by `meteobroker_client_sync` agents, `meteobroker` will query the OEF for
`weather_data` service (proposed by regular `meotestation`s), chose the one with lowest price
propose the price plus a commission to its `meteobroker_client`, and buys from selected `meteostation`
only if `meteobroker_client` accepts the offer.
```bash
# start broker in a new terminal
$ docker exec -it $(docker ps | grep tutorial | awk '{ print $1 }')  bash
root@97689a36f6c9:~/dev/OEFCorePython/examples# python3 weather_broker/meteobroker.py

# start meteostation in new terminal
$ docker exec -it $(docker ps | grep tutorial | awk '{ print $1 }')  bash
root@97689a36f6c9:~/dev/OEFCorePython/examples# python3 weather/meteostation_async.py MeteoSt

# start meteo broker client in a new terminal
root@97689a36f6c9:~/dev/OEFCorePython/examples# python3 weather_broker/meteobroker_client.py
```
### Error management
*Not implemented yet ...*



## 3. OEF-core & agent layer for SDK developers
**This final part** of the tutorial is targeted to OEF-core SDK developers and is language-agnostic. 
It can also be useful for (Python) agents developers to get a better understanding of how things 
work internally behind the scenes, although is completely optional.

### OEF-core low-level communication protocol
The lowest-level operations of the OEF-core are `_send_message` and `_areceive_encoded_message` data. 
To send or receive data to or from the OEF-core you need to have an established 
TCP session to the OEF-core listening socket.
For efficiency and portability reasons, the OEF-core uses a binary wire protocol. If you want to send any
data to the OEF-core you need first to serialize it to binary format (C memory representation of data),
send its size in number of bytes, and then send the actual data serialized. Same apply respectively 
for receiving data from the OEF-core. 

![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/sequence-diagram-send.png "Sequence Diagram Send")

[//]: # (source https://www.websequencediagrams.com/ )

### OEF-core data serialization protocol
The OEF-core uses Google's protocol buffers as a data serialization library. 
Hence, to write an OEF-core agent SDK, make sure an implementation of atleast `SerializeToString()`
and `ParseFromString()` methods are available in your target programming language, or provide it otherwise.

More importantly, throughout its interface, protocol buffers also defines a higher level
abstraction for data exchanges as `message`s. Indeed, the proto files along with rpc calls define a contract 
for interactions between
the OEF-core and SDK and agents developers.


### OEF-core operations
1. `connect()` must be the first operation an agent executes.
It is two steps: open a socket and connect it to the OEF-core listening socket to establish a TCP session,
identify the agent through `_doHandShake`.

The handshake consists in: (1) sending agent's public key (2) receive a random phrase from the OEF-core 
(3) encrypting it using matching private key and send it back to the OEF-core. 
The OEF-core will send a boolean message as an answer indicating the status of the connection.

*Note: encryption and verification are not implemented yet.*

![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/sequence-diagram-connect-2.png "Sequence Diagram Connect")

[//]: # (source https://liveuml.com/diagram/edit/5bbf97c39543831f43b77438 )

2. `register_service()` and `aregister_service()`

![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/sequence-diagram-register-2.png "Sequence Diagram Register")

[//]: # (source https://liveuml.com/diagram/edit/5bbf9eea9543831f43b77439 )

3. `search_services()` and `asearch_services()`

![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/sequence-diagram-query-2.png "Sequence Diagram Query")

[//]: # (source https://liveuml.com/diagram/edit/5bbfa1999543831f43b7743a )

4. `search_agents()`

*Note: not implemented Yet.*

### Conversation operations
1. `Conversation.send() and Conversation.receive()`


![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/sequence-diagram-conversation-2.png "Sequence Diagram Conversation")

[//]: # (source https://liveuml.com/diagram/edit/5bbfa76b9543831f43b7743b9 )


### Agent layer internals

*TODO*

![alt text](https://github.com/uvue-git/OEFCorePython/wiki/imgs/agent-internals.png "Agent layer internals")

[//]: # (source https://whiteboardfox.com/162659-6953-5058 )




>>>>>>> alt
