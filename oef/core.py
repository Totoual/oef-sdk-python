# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from oef import agent_pb2 as agent_pb2
from oef.messages import CFP_TYPES, PROPOSE_TYPES
from oef.query import Query
from oef.schema import Description

logger = logging.getLogger(__name__)


class AgentInterface(ABC):
    """
    An interface that every agent should implement.
    The methods of this interface are the callbacks that are called from the OEFProxy
    when a certain message is sent to the agent.
    The names of the method match the pattern "on_" followed by the name of the message.
    """

    @abstractmethod
    def on_message(self, origin: str,
                   dialogue_id: int,
                   content: bytes):
        """
        Handler for simple messages.

        :param origin: the identifier of the agent who sent the message.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param content: the content of the message (in bytes).
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def on_cfp(self, origin: str,
               dialogue_id: int,
               msg_id: int,
               target: int,
               query: CFP_TYPES):
        """
        Handler for CFP messages.

        :param origin: the identifier of the agent who sent the message.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param msg_id: the message identifier for the dialogue.
        :param target: the identifier of the message to whom this message is answering.
        :param query: the query associated with the Call For Proposals.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def on_propose(self, origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int,
                   proposal: PROPOSE_TYPES):
        """
        Handler for Propose messages.

        :param origin: the identifier of the agent who sent the message.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param msg_id: the message identifier for the dialogue.
        :param target: the identifier of the message to whom this message is answering.
        :param proposal: the proposal associated with the message.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def on_accept(self, origin: str,
                  dialogue_id: int,
                  msg_id: int,
                  target: int, ):
        """
        Handler for Accept messages.

        :param origin: the identifier of the agent who sent the message.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param msg_id: the message identifier for the dialogue.
        :param target: the identifier of the message to whom this message is answering.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def on_decline(self, origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int, ):
        """
        Handler for Decline messages.

        :param origin: the identifier of the agent who sent the message.
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param msg_id: the message identifier for the dialogue.
        :param target: the identifier of the message to whom this message is answering.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def on_error(self, operation: agent_pb2.Server.AgentMessage.Error.Operation,
                 dialogue_id: int,
                 message_id: int):
        """
        Handler for Error messages.

        :param operation: the operation
        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param message_id: the message identifier for the dialogue.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def on_search_result(self, search_id: int, agents: List[str]):
        """
        Handler for Search Result messages.

        :param search_id: the identifier of the search to whom the result is answering.
        :param agents: the list of identifiers of the agents compliant with the search constraints.
        :return:
        """
        raise NotImplementedError


class OEFMethods(ABC):

    @abstractmethod
    def register_agent(self, agent_description: Description) -> bool:
        """
        Adds a description of an agent to the OEF so that it can be understood/ queried by
        other agents in the OEF.

        :param agent_description: description of the agent to add
        :returns: | `True` if agent is successfully added, `False` otherwise. Can fail if such an
                  | agent already exists in the OEF.
        """
        raise NotImplementedError

    @abstractmethod
    def register_service(self, service_description: Description):
        """
        Adds a description of the respective service so that it can be understood/ queried by
        other agents in the OEF.

        :param service_description: description of the services to add
        :returns: `True` if service is successfully added, `False` otherwise. Can fail if such an
        service already exists in the OEF.
        """
        raise NotImplementedError

    @abstractmethod
    def search_agents(self, search_id: int, query: Query) -> None:
        """
        Allows an agent to search for other agents it is interested in communicating with. This can
        be useful when an agent wishes to directly proposition the provision of a service that it
        thinks another agent may wish to be able to offer it. All matching agents are returned
        (potentially including ourself)

        :param search_id: the identifier of the search to whom the result is answering.
        :param query: specifications of the constraints on the agents that are matched
        :returns: a list of the matching agents
        """
        raise NotImplementedError

    @abstractmethod
    def search_services(self, search_id: int, query: Query) -> None:
        """
        Allows an agent to search for a particular service. This allows constrained search of all
        services that have been registered with the OEF. All matching services will be returned
        (potentially including services offered by ourself)

        :param search_id: the identifier of the search to whom the result is answering.
        :param query: the constraint on the matching services
        """
        raise NotImplementedError

    @abstractmethod
    def unregister_agent(self) -> bool:
        """
        Removes the description of an agent from the OEF. This agent will no longer be queryable
        by other agents in the OEF. A conversation handler must be provided that allows the agent
        to receive and manage conversations from other agents wishing to communicate with it.

        :returns: `True` if agent is successfully removed, `False` otherwise. Can fail if
                  such an agent is not registered with the OEF.
        """
        raise NotImplementedError

    @abstractmethod
    def unregister_service(self, service_description: Description) -> None:
        """
        Adds a description of the respective service so that it can be understood/ queried by
        other agents in the OEF.

        :param service_description: description of the services to add
        :returns: `True` if service is successfully added, `False` otherwise. Can fail if such an
                  service already exists in the OEF.
        """
        raise NotImplementedError

    @abstractmethod
    def send_message(self, dialogue_id: int, destination: str, msg: bytes) -> None:
        """
        Send a simple message.

        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param msg: the message (in bytes).
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def send_cfp(self, dialogue_id: int, destination: str, query: CFP_TYPES, msg_id: Optional[int] = 1,
                 target: Optional[int] = 0) -> None:
        """
        Send a Call-For-Proposals.

        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param query: the query associated with the Call For Proposals.
        :param msg_id: the message identifier for the dialogue.
        :param target: the identifier of the message to whom this message is answering.
        :return:
        """

        raise NotImplementedError

    @abstractmethod
    def send_propose(self, dialogue_id: int, destination: str, proposals: PROPOSE_TYPES, msg_id: int,
                     target: Optional[int] = None):
        """
        Send a Propose.

        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param proposals:
        :param msg_id: the message identifier for the dialogue.
        :param target: the identifier of the message to whom this message is answering.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def send_accept(self, dialogue_id: int, destination: str, msg_id: int,
                    target: Optional[int] = None):
        """
        Send an Accept.

        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param msg_id: the message identifier for the dialogue.
        :param target: the identifier of the message to whom this message is answering.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def send_decline(self, dialogue_id: int, destination: str, msg_id: int,
                     target: Optional[int] = None):
        """
        Send a Decline.

        :param dialogue_id: the identifier of the dialogue in which the message is sent.
        :param destination: the agent identifier to whom the message is sent.
        :param msg_id: the message identifier for the dialogue.
        :param target: the identifier of the message to whom this message is answering.
        :return:
        """
        raise NotImplementedError


class OEFProxy(OEFMethods):

    def __init__(self, public_key):
        self._public_key = public_key

    @property
    def public_key(self) -> str:
        return self._public_key

    @abstractmethod
    async def connect(self):
        """Connect to the OEF Node."""
        raise NotImplementedError

    @abstractmethod
    async def _receive(self) -> bytes:
        """
        Receive a message from the OEF Node.

        :return: the bytes received from the communication channel.
        """
        raise NotImplementedError

    async def loop(self, agent: AgentInterface):
        """
        Event loop to wait for messages and to dispatch the arrived messages to the proper handler.

        :param agent: the implementation of the message handlers specified in AgentInterface.
        :return:
        """
        while True:
            try:
                data = await self._receive()
            except asyncio.CancelledError:
                logger.debug("Proxy {}: loop cancelled".format(self.public_key))
                break
            msg = agent_pb2.Server.AgentMessage()
            msg.ParseFromString(data)
            case = msg.WhichOneof("payload")
            logger.debug("loop {0}".format(case))
            if case == "agents":
                agent.on_search_result(msg.agents.search_id, msg.agents.agents)
            elif case == "error":
                agent.on_error(msg.error.operation, msg.error.dialogue_id, msg.error.msg_id)
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
