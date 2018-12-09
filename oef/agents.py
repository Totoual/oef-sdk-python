# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import asyncio
import logging
from abc import ABC
from typing import Optional

from oef.core import OEFProxy, AgentInterface
from oef.proxy import OEFNetworkProxy, PROPOSE_TYPES, CFP_TYPES, OEFLocalProxy
from oef.query import Query
from oef.schema import Description

logger = logging.getLogger(__name__)


class Agent(AgentInterface, ABC):

    @property
    def public_key(self):
        return self.oef_proxy.public_key

    def __init__(self, oef_proxy: OEFProxy):
        self.oef_proxy = oef_proxy
        self._task = None
        self._loop = asyncio.get_event_loop()

    def run(self):
        self._loop.run_until_complete(self.async_run())

    def stop(self):
        """Stop the agent. Specifically, if ``run()`` or ``async_run()`` have been called, then
        this method will cancel the previously instantiated task.
        The agent will be stopped as soon as possible, depending on the proxy loop."""
        if self._task:
            self._task.cancel()

    async def async_run(self):
        self._task = asyncio.ensure_future(self.oef_proxy.loop(self))
        await self._task

    def connect(self) -> None:
        """Connect the agent to the OEF Node specified by ``oef_addr`` and ``_oef_port``"""
        logger.debug("{}: Connecting...".format(self.public_key))
        self._loop.run_until_complete(self.oef_proxy.connect())
        logger.debug("{}: Connection established.".format(self.public_key))

    def register_agent(self, agent_description: Description) -> None:
        self.oef_proxy.register_agent(agent_description)

    def unregister_agent(self) -> None:
        self.oef_proxy.unregister_agent()

    def register_service(self, service_description: Description) -> None:
        self.oef_proxy.register_service(service_description)

    def unregister_service(self, service_description: Description) -> None:
        self.oef_proxy.unregister_service(service_description)

    def search_agents(self, search_id: int, query: Query) -> None:
        self.oef_proxy.search_agents(search_id, query)

    def search_services(self, search_id: int, query: Query) -> None:
        self.oef_proxy.search_services(search_id, query)

    def send_message(self,
                     dialogue_id: int,
                     destination: str,
                     msg: bytes):
        logger.debug("Agent {}: dialogue_id={}, destination={}, msg={}"
                     .format(self.public_key,
                             dialogue_id,
                             destination,
                             msg))
        self.oef_proxy.send_message(dialogue_id, destination, msg)

    def send_cfp(self,
                 dialogue_id: int,
                 destination: str,
                 query: CFP_TYPES,
                 msg_id: Optional[int] = 1,
                 target: Optional[int] = 0):
        logger.debug("Agent {}: dialogue_id={}, destination={}, query={}, msg_id={}, target={}"
                     .format(self.public_key,
                             dialogue_id,
                             destination,
                             query,
                             msg_id,
                             target))
        self.oef_proxy.send_cfp(dialogue_id, destination, query, msg_id, target)

    def send_propose(self,
                     dialogue_id: int,
                     destination: str,
                     proposals: PROPOSE_TYPES,
                     msg_id: int,
                     target: Optional[int] = None):
        logger.debug("Agent {}: dialogue_id={}, destination={}, proposals={}, msg_id={}, target={}"
                     .format(self.public_key,
                             dialogue_id,
                             destination,
                             proposals,
                             msg_id,
                             target))
        self.oef_proxy.send_propose(dialogue_id, destination, proposals, msg_id, target)

    def send_accept(self, dialogue_id: int,
                    destination: str,
                    msg_id: int,
                    target: Optional[int] = None):
        logger.debug("Agent {}: dialogue_id={}, destination={}, msg_id={}, target={}"
                     .format(self.public_key,
                             dialogue_id,
                             destination,
                             msg_id,
                             target))
        self.oef_proxy.send_accept(dialogue_id, destination, msg_id, target)

    def send_decline(self, dialogue_id: int,
                     destination: str,
                     msg_id: int,
                     target: Optional[int] = None):
        logger.debug("Agent {}: dialogue_id={}, destination={}, msg_id={}, target={}"
                     .format(self.public_key,
                             dialogue_id,
                             destination,
                             msg_id,
                             target))
        self.oef_proxy.send_decline(dialogue_id, destination, msg_id, target)


class OEFAgent(Agent):
    """Agent that interacts with an OEFNode on the network."""

    def __init__(self, public_key: str, oef_addr: str, oef_port: int = 3333) -> None:
        """
        Initialize an OEF network agent.
        :param public_key: the public key (identifier) of the agent
        :param oef_addr: the IP address of the OEF Node.
        :param oef_port: the port for the connection.
        """
        self._oef_addr = oef_addr
        self._oef_port = oef_port
        super().__init__(OEFNetworkProxy(public_key, str(self._oef_addr), self._oef_port))


class LocalAgent(Agent):
    """Agent that interacts with a local implementation of an OEF Node."""

    def __init__(self, public_key: str, local_node: OEFLocalProxy.LocalNode):
        """
        Initialize an OEF local agent.
        :param public_key: the public key (identifier) of the agent.
        :param local_node: an instance of the local implementation of the OEF Node.
        """
        super().__init__(OEFLocalProxy(public_key, local_node))
