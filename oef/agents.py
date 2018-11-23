# vim: set number autoindent tabstop=2 expandtab :
# Company: FETCH.ai
# Author: Lokman Rahmani
# Creation: 26/09/18
#
# This file implements python OEF agent SDK oef.agent submodule
# It provides:
#   - low-level functions: _send_message() and _areceive_encoded_message()
#      to send and receive oef.message-s to and from OEF core
#   - high-level functions: _connectOEF(), RegisterDataModelInstance(),
#      sendsearch_services(), aWaitCFPProposal(), sendCFProposal(), 
#      aWaitProposalAnswer(), sendProposalAnswer(), DeliverProposal(),
#      aWaitProposalDelivery()
#      that implements OEF protocols as functions that facilitate 
#      agent developement
# Type checking:
#   - _send_message() do check if the message to be sent is allowed to be
#     sent from a  white list variable (AUTHORIZED_MSGS)
import asyncio
from abc import ABC

import logging
from typing import List

from oef import agent_pb2
from oef.api import OEFProxy, PROPOSE_TYPES, CFP_TYPES, Description, Query

logger = logging.getLogger(__name__)


def _warning_not_implemented_method(method_name):
    logger.warning("You should implement {} in your OEFAgent class.", method_name)


class OEFAgent(ABC):
    """The abstract definition of an agent."""

    def __init__(self, public_key: str, oef_addr: str, oef_port: int = 3333) -> None:
        self._pubkey = public_key
        self._oef_addr = oef_addr
        self._oef_port = oef_port

        self._loop = asyncio.get_event_loop()
        self._connection = None  # type: OEFProxy

    def connect(self) -> None:
        """Connect the agent to the OEF Node specified by _oef_addr and _oef_port"""
        logger.debug("Start connection to %s:%s", self._oef_addr, self._oef_port)
        self._connection = self._get_connection()
        logger.debug("Connection established to %s:%s", self._oef_addr, self._oef_port)

    def _get_connection(self) -> OEFProxy:
        connection = OEFProxy(self._pubkey, str(self._oef_addr), self._oef_port)
        self._loop.run_until_complete(connection.connect())
        return connection

    def run(self):
        self._loop.run_until_complete(self._connection.loop(self))

    def on_cfp(self, origin: str,
               conversation_id: str,
               fipa_message_id: int,
               fipa_target: int,
               query: CFP_TYPES):
        logger.info("on_cfp: {}, {}, {}, {}", origin, conversation_id, fipa_message_id, fipa_target, query)
        _warning_not_implemented_method(self.on_cfp.__name__)

    def on_accept(self, origin: str,
                  conversation_id: str,
                  fipa_message_id: int,
                  fipa_target: int, ):
        logger.info("on_accept: {}, {}, {}, {}", origin, conversation_id, fipa_message_id, fipa_target)
        _warning_not_implemented_method(self.on_accept.__name__)

    def on_decline(self, origin: str,
                   conversation_id: str,
                   fipa_message_id: int,
                   fipa_target: int, ):
        logger.info("on_decline: {}, {}, {}, {}", origin, conversation_id, fipa_message_id, fipa_target)
        _warning_not_implemented_method(self.on_decline.__name__)

    def on_propose(self, origin: str,
                   conversation_id: str,
                   fipa_message_id: int,
                   fipa_target: int,
                   proposal: PROPOSE_TYPES):
        logger.info("on_propose: {}, {}, {}, {}, {}", origin, conversation_id, fipa_message_id, fipa_target, proposal)
        _warning_not_implemented_method(self.on_propose.__name__)

    def on_error(self, operation: agent_pb2.Server.AgentMessage.Error.Operation, conversation_id: str, message_id: int):
        logger.info("on_error: {}, {}, {}", operation, conversation_id, message_id)
        _warning_not_implemented_method(self.on_error.__name__)

    def on_message(self, origin: str, conversation_id: str, content: bytes):
        logger.info("on_message: {}, {}, {}, {}", origin, conversation_id, content)
        _warning_not_implemented_method(self.on_message.__name__)

    def on_search_result(self, agents: List[str]):
        logger.info("on_search_result: {}", agents)
        _warning_not_implemented_method(self.on_search_result.__name__)

    def register_agent(self, agent_description: Description) -> bool:
        """
        Adds a description of an agent to the OEF so that it can be understood/ queried by
        other agents in the OEF.

        :param agent_description: description of the agent to add
        :returns: `True` if agent is successfully added, `False` otherwise. Can fail if such an
        agent already exists in the OEF.
        """
        self._connection.register_agent(agent_description)

    def unregister_agent(self, agent_description: Description) -> bool:
        """
        Removes the description of an agent from the OEF. This agent will no longer be queryable
        by other agents in the OEF. A conversation handler must be provided that allows the agent
        to receive and manage conversations from other agents wishing to communicate with it.

        :param agent_description: description of the agent to remove
        :returns: `True` if agent is successfully removed, `False` otherwise. Can fail if
        such an agent is not registered with the OEF.
        """
        self._connection.unregister_agent(agent_description)

    def register_service(self, service_description: Description):
        """
        Adds a description of the respective service so that it can be understood/ queried by
        other agents in the OEF.
        :param service_description: description of the services to add
        :returns: `True` if service is successfully added, `False` otherwise. Can fail if such an
        service already exists in the OEF.
        """
        self._connection.register_service(service_description)

    def unregister_service(self, service_description: Description) -> None:
        """
        Adds a description of the respective service so that it can be understood/ queried by
        other agents in the OEF.
        :param service_description: description of the services to add
        :returns: `True` if service is successfully added, `False` otherwise. Can fail if such an
        service already exists in the OEF.
        """
        self._connection.unregister_service(service_description)

    def search_agents(self, query: Query) -> None:
        """
        Allows an agent to search for other agents it is interested in communicating with. This can
        be useful when an agent wishes to directly proposition the provision of a service that it
        thinks another agent may wish to be able to offer it. All matching agents are returned
        (potentially including ourself)
        :param query: specifications of the constraints on the agents that are matched
        :returns: a list of the matching agents
        """
        self._connection.search_agents(query)

    def search_services(self, query: Query) -> None:
        """
        Allows an agent to search for a particular service. This allows constrained search of all
        services that have been registered with the OEF. All matching services will be returned
        (potentially including services offered by ourself)
        :param query: the constraint on the matching services
        """
        self._connection.search_services(query)
