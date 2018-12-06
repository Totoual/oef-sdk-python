# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Tuple, List

from oef import agent_pb2
from oef.agents import Agent
from oef.core import OEFProxy
from oef.messages import CFP_TYPES, PROPOSE_TYPES


class AgentTest(Agent):
    """
    An agent used for tests.
    """

    def __init__(self, proxy: OEFProxy):
        """
        Initialize an Local OEFAgent for tests.
        """
        super().__init__(proxy)
        self.received_msg = []

    def _process_message(self, arguments: Tuple):
        self.received_msg.append(arguments)

    def stop(self):
        if self._task:
            self._task.cancel()

    def on_message(self, origin: str, dialogue_id: int, content: bytes):
        self._process_message((origin, dialogue_id, content))

    def on_search_result(self, search_id: int, agents: List[str]):
        pass

    def on_cfp(self,
               origin: str,
               dialogue_id: int,
               msg_id: int,
               target: int,
               query: CFP_TYPES):
        self._process_message((origin, dialogue_id, msg_id, target, query))

    def on_propose(self,
                   origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int,
                   proposal: PROPOSE_TYPES):
        self._process_message((origin, dialogue_id, msg_id, target, proposal))

    def on_accept(self,
                  origin: str,
                  dialogue_id: int,
                  msg_id: int,
                  target: int):
        self._process_message((origin, dialogue_id, msg_id, target))

    def on_decline(self,
                   origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int):
        self._process_message((origin, dialogue_id, msg_id, target))

    def on_error(self,
                 operation: agent_pb2.Server.AgentMessage.Error.Operation,
                 dialogue_id: int,
                 message_id: int):
        pass
