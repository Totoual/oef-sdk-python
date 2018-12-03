# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""
Python bindings for OEFCore
"""

import asyncio
import logging
from collections import defaultdict

import oef.agent_pb2 as agent_pb2

import struct

from typing import Optional, Awaitable, Tuple, Dict

from oef.core import AgentInterface, OEFProxy, OEFMethods
from oef.messages import SimpleMessage, CFP_TYPES, PROPOSE_TYPES, CFP, Propose, Accept, Decline, Message
from oef.schema import Description
from oef.query import Query

logger = logging.getLogger(__name__)


DEFAULT_OEF_NODE_PORT = 3333


class OEFNetworkProxy(OEFProxy):
    """
    Proxy to the functionality of the OEF. Provides functionality for an agent to:

     * Register a description of itself
     * Register its services
     * Locate other agents
     * Locate other services
     * Establish a connection with another agent
    """

    def __init__(self, public_key: str, oef_addr: str, port: int = DEFAULT_OEF_NODE_PORT) -> None:
        """
        Initialize the proxy to the OEF Node.

        :param public_key: the public key used in the protocols.
        :param oef_addr: the IP address of the OEF node.
        :param port: port number for the connection.
        """
        super().__init__(public_key)

        self.oef_addr = oef_addr
        self.port = port

        # these are setup in _connect_to_server
        self._connection = None
        self._server_reader = None
        self._server_writer = None

    async def _connect_to_server(self, event_loop) -> Awaitable[Tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
        return await asyncio.open_connection(self.oef_addr, self.port, loop=event_loop)

    def _send(self, protobuf_msg):  # async too ?
        serialized_msg = protobuf_msg.SerializeToString()
        nbytes = struct.pack("I", len(serialized_msg))
        self._server_writer.write(nbytes)
        self._server_writer.write(serialized_msg)

    async def _receive(self):
        nbytes_packed = await self._server_reader.read(len(struct.pack("I", 0)))
        logger.debug("received ${0}".format(nbytes_packed))
        nbytes = struct.unpack("I", nbytes_packed)
        logger.debug("received unpacked ${0}".format(nbytes[0]))
        logger.debug("Preparing to receive ${0} bytes ...".format(nbytes[0]))
        return await self._server_reader.read(nbytes[0])

    async def connect(self) -> bool:
        """Connect to the OEFNode"""

        if self._connection is not None:
            return True

        event_loop = asyncio.get_event_loop()
        self._connection = await self._connect_to_server(event_loop)
        self._server_reader, self._server_writer = self._connection
        # Step 1: Agent --(ID)--> OEFCore
        pb_public_key = agent_pb2.Agent.Server.ID()
        pb_public_key.public_key = self.public_key
        self._send(pb_public_key)
        # Step 2: OEFCore --(Phrase)--> Agent
        data = await self._receive()
        pb_phrase = agent_pb2.Server.Phrase()
        pb_phrase.ParseFromString(data)
        case = pb_phrase.WhichOneof("payload")
        if case == "failure":
            return False
        # Step 3: Agent --(Answer)--> OEFCore
        pb_answer = agent_pb2.Agent.Server.Answer()
        pb_answer.answer = pb_phrase.phrase[::-1]
        self._send(pb_answer)
        # Step 4: OEFCore --(Connected)--> Agent
        data = await self._receive()
        pb_status = agent_pb2.Server.Connected()
        pb_status.ParseFromString(data)
        return pb_status.status

    def register_agent(self, agent_description: Description) -> bool:
        envelope = agent_pb2.Envelope()
        envelope.register_description.CopyFrom(agent_description.to_pb())
        self._send(envelope)

    def register_service(self, service_description: Description):
        envelope = agent_pb2.Envelope()
        envelope.register_service.CopyFrom(service_description.to_pb())
        self._send(envelope)

    def unregister_agent(self) -> bool:
        envelope = agent_pb2.Envelope()
        envelope.unregister_description.CopyFrom(agent_pb2.Envelope.Nothing())
        self._send(envelope)

    def unregister_service(self, service_description: Description) -> None:
        envelope = agent_pb2.Envelope()
        envelope.unregister_service.CopyFrom(service_description.to_pb())
        self._send(envelope)

    def search_agents(self, search_id: int, query: Query) -> None:
        envelope = agent_pb2.Envelope()
        envelope.search_agents.query.CopyFrom(query.to_pb())
        envelope.search_agents.search_id = search_id
        self._send(envelope)

    def search_services(self, search_id: int, query: Query) -> None:
        envelope = agent_pb2.Envelope()
        envelope.search_services.query.CopyFrom(query.to_pb())
        envelope.search_services.search_id = search_id
        self._send(envelope)

    def send_message(self, dialogue_id: int, destination: str, msg: bytes):
        msg = SimpleMessage(dialogue_id, destination, msg)
        self._send(msg.to_envelope())

    def send_cfp(self,
                 dialogue_id: int,
                 destination: str,
                 query: CFP_TYPES,
                 msg_id: Optional[int] = 1,
                 target: Optional[int] = 0):
        msg = CFP(dialogue_id, destination, query, msg_id, target)
        self._send(msg.to_envelope())

    def send_propose(self, dialogue_id: int, destination: str, proposals: PROPOSE_TYPES, msg_id: int,
                     target: Optional[int] = None):

        msg = Propose(dialogue_id, destination, proposals, msg_id, target)
        self._send(msg.to_envelope())

    def send_accept(self, dialogue_id: int, destination: str, msg_id: int,
                    target: Optional[int] = None):
        msg = Accept(dialogue_id, destination, msg_id, target)
        self._send(msg.to_envelope())

    def send_decline(self,
                     dialogue_id: int,
                     destination: str,
                     msg_id: int,
                     target: Optional[int] = None):
        msg = Decline(dialogue_id, destination, msg_id, target)
        self._send(msg.to_envelope())

    def close(self) -> None:
        """
        Used to tear down resources associated with this Proxy, i.e. the writing connection with
        the server.
        """
        self._server_writer.close()

    async def loop(self, agent: AgentInterface) -> None:    # noqa: C901
        """
        Event loop to wait for messages and to dispatch the arrived messages to the proper handler.

        :param agent: the implementation of the message handlers specified in AgentInterface.
        :return:
        """

        while True:
            data = await self._receive()
            msg = agent_pb2.Server.AgentMessage()
            msg.ParseFromString(data)
            case = msg.WhichOneof("payload")
            logger.debug("loop {0}".format(case))
            if case == "agents":
                agent.on_search_result(msg.agents.search_id, msg.agents.agents)
            elif case == "error":
                agent.on_error(msg.error.operation, msg.error.dialogue_id, msg.error.msgid)
            elif case == "content":
                content_case = msg.content.WhichOneof("payload")
                logger.debug("msg content {0}".format(content_case))
                if content_case == "content":
                    agent.on_message(msg.content.origin, msg.content.dialogue_id, msg.content.content)
                elif content_case == "fipa":
                    fipa = msg.content.fipa
                    fipa_case = fipa.WhichOneof("msg")
                    if fipa_case == "cfp":
                        cfp_case = fipa.cfp.WhichOneof("payload")
                        if cfp_case == "nothing":
                            query = None
                        elif cfp_case == "content":
                            query = fipa.cfp.content
                        elif cfp_case == "query":
                            query = Query.from_pb(fipa.cfp.query)
                        else:
                            raise Exception("Query type not valid.")
                        agent.on_cfp(msg.content.origin, msg.content.dialogue_id, fipa.msg_id, fipa.target, query)
                    elif fipa_case == "propose":
                        propose_case = fipa.propose.WhichOneof("payload")
                        if propose_case == "content":
                            proposals = fipa.propose.content
                        else:
                            proposals = [Description.from_pb(propose) for propose in fipa.propose.proposals.objects]
                        agent.on_propose(msg.content.origin, msg.content.dialogue_id, fipa.msg_id, fipa.target,
                                        proposals)
                    elif fipa_case == "accept":
                        agent.on_accept(msg.content.origin, msg.content.dialogue_id, fipa.msg_id, fipa.target)
                    elif fipa_case == "decline":
                        agent.on_decline(msg.content.origin, msg.content.dialogue_id, fipa.msg_id, fipa.target)
                    else:
                        logger.warning("Not implemented yet: fipa {0}".format(fipa_case))


class OEFLocalProxy(OEFProxy):
    """
    Proxy to the functionality of the OEF.
    It allows the interaction between agents, but not the search functionality.
    It is useful for local testing.
    """

    class LocalNode:
        """A light-weight implementation of a OEF Node."""

        def __init__(self):
            self.agents = dict()                     # Dict[str, Description]
            self.services = defaultdict(lambda: [])  # Dict[str, List[Description]]
            self._lock = asyncio.Lock()

            self.queues: Dict[str, asyncio.Queue] = {}
            self.loop = asyncio.get_event_loop()

        def connect(self, public_key: str) -> asyncio.Queue:
            queue = asyncio.Queue()
            self.queues[public_key] = queue
            return queue

        def register_agent(self, public_key: str, agent_description: Description) -> bool:
            self.loop.run_until_complete(self._lock.acquire())
            self.agents[public_key] = agent_description
            self._lock.release()

        def register_service(self, public_key: str, service_description: Description):
            self.loop.run_until_complete(self._lock.acquire())
            self.services[public_key].append(service_description)
            self._lock.release()

        def search_agents(self, public_key: str, search_id: int, query: Query) -> None:
            raise NotImplementedError

        def search_services(self, public_key: str, search_id: int, query: Query) -> None:
            raise NotImplementedError

        def unregister_agent(self, public_key: str) -> bool:
            self.loop.run_until_complete(self._lock.acquire())
            self.agents.pop(public_key)
            self._lock.release()

        def unregister_service(self, public_key: str, service_description: Description) -> None:
            self.loop.run_until_complete(self._lock.acquire())
            self.agents[public_key].remove(service_description)
            self._lock.release()

        def _send(self, public_key: str, msg: Message):
            e = msg.to_envelope()
            destination = e.send_message.destination

            new_msg = agent_pb2.Server.AgentMessage()
            new_msg.content.origin = public_key
            new_msg.content.dialogue_id = e.send_message.dialogue_id

            payload = e.send_message.WhichOneof("payload")
            if payload == "content":
                new_msg.content.content = e.send_message.content
            elif payload == "fipa":
                new_msg.content.fipa.CopyFrom(e.send_message.fipa)

            self.queues[destination].put_nowait(new_msg.SerializeToString())

        def send_message(self, public_key: str, dialogue_id: int, destination: str, msg: bytes) -> None:
            msg = SimpleMessage(dialogue_id, destination, msg)
            self._send(public_key, msg)

        def send_cfp(self, public_key: str, dialogue_id: int, destination: str, query: CFP_TYPES, msg_id: Optional[int] = 1,
                     target: Optional[int] = 0) -> None:
            msg = CFP(dialogue_id, destination, query, msg_id, target)
            self._send(public_key, msg)

        def send_propose(self, public_key: str, dialogue_id: int, destination: str, proposals: PROPOSE_TYPES, msg_id: int,
                         target: Optional[int] = None):
            msg = Propose(dialogue_id, destination, proposals, msg_id, target)
            self._send(public_key, msg)

        def send_accept(self, public_key: str, dialogue_id: int, destination: str, msg_id: int, target: Optional[int] = None):
            msg = Accept(dialogue_id, destination, msg_id, target)
            self._send(public_key, msg)

        def send_decline(self, public_key: str, dialogue_id: int, destination: str, msg_id: int, target: Optional[int] = None):
            msg = Decline(dialogue_id, destination, msg_id, target)
            self._send(public_key, msg)

    def __init__(self, public_key: str, local_node: LocalNode):
        super().__init__(public_key)
        self.local_node = local_node
        self.read_queue: asyncio.Queue = None

    def register_agent(self, agent_description: Description) -> bool:
        self.local_node.register_agent(self.public_key, agent_description)

    def register_service(self, service_description: Description):
        self.local_node.register_service(self.public_key, service_description)

    def search_agents(self, search_id: int, query: Query) -> None:
        self.local_node.search_agents(self.public_key, search_id, query)

    def search_services(self, search_id: int, query: Query) -> None:
        self.local_node.search_services(self.public_key, search_id, query)

    def unregister_agent(self) -> bool:
        self.local_node.unregister_agent(self.public_key)

    def unregister_service(self, service_description: Description) -> None:
        self.local_node.unregister_service(self.public_key, service_description)

    def send_message(self, dialogue_id: int, destination: str, msg: bytes) -> None:
        self.local_node.send_message(self.public_key, dialogue_id, destination, msg)

    def send_cfp(self, dialogue_id: int, destination: str, query: CFP_TYPES, msg_id: Optional[int] = 1,
                 target: Optional[int] = 0) -> None:
        self.local_node.send_cfp(self.public_key, dialogue_id, destination, query, msg_id)

    def send_propose(self, dialogue_id: int, destination: str, proposals: PROPOSE_TYPES, msg_id: int,
                     target: Optional[int] = None):
        self.local_node.send_propose(self.public_key, dialogue_id, destination, proposals, msg_id, target)

    def send_accept(self, dialogue_id: int, destination: str, msg_id: int, target: Optional[int] = None):
        self.local_node.send_accept(self.public_key, dialogue_id, destination, msg_id, target)

    def send_decline(self, dialogue_id: int, destination: str, msg_id: int, target: Optional[int] = None):
        self.local_node.send_decline(self.public_key, dialogue_id, destination, msg_id, target)

    def connect(self):
        queue = self.local_node.connect(self.public_key)
        self.read_queue = queue

    async def _receive(self):
        data = await self.read_queue.get()
        return data

    async def loop(self, agent: AgentInterface):
        while True:
            data = await self._receive()
            msg = agent_pb2.Server.AgentMessage()
            msg.ParseFromString(data)
            case = msg.WhichOneof("payload")
            logger.debug("loop {0}".format(case))
            if case == "agents":
                agent.on_search_result(msg.agents.search_id, msg.agents.agents)
            elif case == "error":
                agent.on_error(msg.error.operation, msg.error.dialogue_id, msg.error.msgid)
            elif case == "content":
                content_case = msg.content.WhichOneof("payload")
                logger.debug("msg content {0}".format(content_case))
                if content_case == "content":
                    agent.on_message(msg.content.origin, msg.content.dialogue_id, msg.content.content)
                elif content_case == "fipa":
                    fipa = msg.content.fipa
                    fipa_case = fipa.WhichOneof("msg")
                    if fipa_case == "cfp":
                        cfp_case = fipa.cfp.WhichOneof("payload")
                        if cfp_case == "nothing":
                            query = None
                        elif cfp_case == "content":
                            query = fipa.cfp.content
                        elif cfp_case == "query":
                            query = Query.from_pb(fipa.cfp.query)
                        else:
                            raise Exception("Query type not valid.")
                        agent.on_cfp(msg.content.origin, msg.content.dialogue_id, fipa.msg_id, fipa.target, query)
                    elif fipa_case == "propose":
                        propose_case = fipa.propose.WhichOneof("payload")
                        if propose_case == "content":
                            proposals = fipa.propose.content
                        else:
                            proposals = [Description.from_pb(propose) for propose in fipa.propose.proposals.objects]
                        agent.on_propose(msg.content.origin, msg.content.dialogue_id, fipa.msg_id, fipa.target,
                                        proposals)
                    elif fipa_case == "accept":
                        agent.on_accept(msg.content.origin, msg.content.dialogue_id, fipa.msg_id, fipa.target)
                    elif fipa_case == "decline":
                        agent.on_decline(msg.content.origin, msg.content.dialogue_id, fipa.msg_id, fipa.target)
                    else:
                        logger.warning("Not implemented yet: fipa {0}".format(fipa_case))

