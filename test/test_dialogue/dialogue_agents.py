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
from typing import List, Optional, Tuple

from oef.dialogue import GroupDialogues, DialogueAgent, SingleDialogue
from oef.messages import CFP_TYPES, OEFErrorOperation, PROPOSE_TYPES


class SimpleSingleDialogueTest(SingleDialogue):
    """
    A simple specialization of :class:`~oef.dialogue.SingleDialogue`.
    It stores all the messages he receives, so we can track
    the history of the received messages and assert some properties on it.
    """

    def __init__(self, agent: DialogueAgent,
                 destination: str,
                 id_: Optional[int] = None):
        super().__init__(agent, destination, id_)
        self.received_msg = []

    def _process_message(self, arguments: Tuple):
        """Store the message into the state of the agent."""
        self.received_msg.append(arguments)

    def on_message(self, origin: str, dialogue_id: int, content: bytes) -> None:
        self._process_message((origin, dialogue_id, content))

    def on_propose(self, origin: str, dialogue_id: int, msg_id: int, target: int, proposals: PROPOSE_TYPES):
        self._process_message((origin, dialogue_id, msg_id, target, proposals))

    def on_cfp(self, origin: str, dialogue_id: int, msg_id: int, target: int, query: CFP_TYPES) -> None:
        self._process_message((origin, dialogue_id, msg_id, target, query))

    def on_accept(self, origin: str, dialogue_id: int, msg_id: int, target: int) -> None:
        self._process_message((origin, dialogue_id, msg_id, target))

    def on_decline(self, origin: str, dialogue_id: int, msg_id: int, target: int) -> None:
        self._process_message((origin, dialogue_id, msg_id, target))


class GroupDialoguesTest(GroupDialogues):

    def __init__(self, agent: DialogueAgent, agents: List[str]):
        super().__init__(agent)
        dialogues = [SimpleSingleDialogueTest(agent, a) for a in agents]
        self.add_agents(dialogues)

    def better(self, price1: int, price2: int) -> bool:
        return price1 < price2

    def finished(self):
        pass


class ServerAgentDialogueTest(DialogueAgent):

    def on_new_cfp(self, from_: str, dialogue_id: int, msg_id: int, target: int, query: CFP_TYPES) -> None:
        self.register_dialogue(SimpleSingleDialogueTest(self, from_, dialogue_id))
        self.on_cfp(from_, dialogue_id, msg_id, target, query)

    def on_new_message(self, from_: str, dialogue_id: int, content: bytes) -> None:
        self.register_dialogue(SimpleSingleDialogueTest(self, from_, dialogue_id))
        self.on_message(from_, dialogue_id, content)

    def on_connection_error(self, operation: OEFErrorOperation) -> None:
        pass

