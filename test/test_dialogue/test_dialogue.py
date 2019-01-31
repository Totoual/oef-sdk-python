# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
import asyncio
from typing import List, Callable, Optional, Tuple

from oef.core import OEFProxy
from oef.dialogue import DialogueAgent, GroupDialogues, SingleDialogue
from oef.messages import PROPOSE_TYPES, CFP_TYPES, OEFErrorOperation
from oef.proxy import OEFNetworkProxy
from test.conftest import _ASYNCIO_DELAY

from test.common import setup_test_agents, AgentTest


class SingleDialogueTest(SingleDialogue):

    def __init__(self, agent: DialogueAgent,
                 destination: str,
                 notify: Callable,
                 id_: Optional[int] = None):
        super().__init__(agent, destination, id_)
        self.received_msg = []
        self.notify = notify  # type: Callable
        self.data_received = 0
        # self.agent.send_cfp(self.id, destination, None)

    def _process_message(self, arguments: Tuple):
        """Store the message into the state of the agent."""
        self.received_msg.append(arguments)

    def on_message(self, origin: str, dialogue_id: int, content: bytes) -> None:
        self._process_message((origin, dialogue_id, content))
        super().on_message(origin, dialogue_id, content)

    def on_propose(self, origin: str, dialogue_id: int, msg_id: int, target: int, proposals: PROPOSE_TYPES):
        self._process_message((origin, dialogue_id, msg_id, target, proposals))
        super().on_propose(origin, dialogue_id, msg_id, target, proposals)

        assert type(proposals) == list and len(proposals) == 1
        proposal = proposals[0]
        self.notify(self.destination, proposal.values["price"])

    def on_cfp(self, origin: str, dialogue_id: int, msg_id: int, target: int, query: CFP_TYPES) -> None:
        self._process_message((origin, dialogue_id, msg_id, target, query))
        super().on_cfp(origin, dialogue_id, msg_id, target, query)

    def on_accept(self, origin: str, dialogue_id: int, msg_id: int, target: int) -> None:
        self._process_message((origin, dialogue_id, msg_id, target))
        super().on_accept(origin, dialogue_id, msg_id, target)

    def on_decline(self, origin: str, dialogue_id: int, msg_id: int, target: int) -> None:
        self._process_message((origin, dialogue_id, msg_id, target))
        super().on_decline(origin, dialogue_id, msg_id, target)


class GroupDialoguesTest(GroupDialogues):

    def __init__(self, agent: DialogueAgent, agents: List[str]):
        super().__init__(agent)
        dialogues = [SingleDialogueTest(agent, a, lambda from_, price: self.update(from_, price)) for a in agents]
        self.add_agents(dialogues)

    def better(self, price1: int, price2: int) -> bool:
        return price1 < price2

    def finished(self):
        pass


class ServerAgentDialogueTest(DialogueAgent):

    def on_new_cfp(self, from_: str, dialogue_id: int, msg_id: int, target: int, query: CFP_TYPES) -> None:
        pass

    def on_new_message(self, from_: str, dialogue_id: int, content: str) -> None:
        pass

    def on_connection_error(self, operation: OEFErrorOperation) -> None:
        pass


class TestSimpleMessage:

    def test_on_message(self):

        with setup_test_agents(1, False, prefix="dialogues_on_message") as agent:
            agent_0 = agent[0]  # type: AgentTest
            dialogue_agent_0 = ServerAgentDialogueTest(OEFNetworkProxy("dialogue_agent_0", "127.0.0.1"))

            agent_0.connect()
            dialogue_agent_0.connect()

            agent_0.send_message(0, 0, "dialogue_agent_0", b"message")

            asyncio.ensure_future(asyncio.gather(
                agent_0.async_run(),
                dialogue_agent_0.async_run()
            ))
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))










