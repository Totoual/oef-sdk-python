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

from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Optional

from oef.messages import CFP_TYPES, PROPOSE_TYPES

from oef import agent_pb2
from oef.agents import Agent
from oef.core import DialogueInterface, OEFProxy

import uuid

DialogueKey = Tuple[str, int]
DialogueAgent = None


class SingleDialogue(DialogueInterface, ABC):

    def __init__(self, agent: DialogueAgent,
                 destination: str,
                 id_: Optional[int] = None):
        self.agent = agent
        self.destination = destination
        self.id = id_
        if id_:
            self.is_buyer = False
        else:
            self.id = uuid.uuid4().time_mid
            self.is_buyer = True

    @abstractmethod
    def on_error(self):
        pass

    def key(self) -> DialogueKey:
        return self.destination, self.id


class DialogueAgent(Agent, ABC):

    def __init__(self, oef_proxy: OEFProxy):
        super().__init__(oef_proxy)
        self.dialogues = {}  # type: Dict[DialogueKey, SingleDialogue]

    def register_dialogue(self, dialogue: SingleDialogue) -> None:
        dialogue_key = dialogue.key()
        try:
            assert dialogue_key not in self.dialogues
        except AssertionError:
            raise Exception("Dialogue key {} already in use.".format(dialogue_key))
        self.dialogues[dialogue_key] = dialogue

    def unregister_dialogue(self, dialogue: SingleDialogue) -> None:
        dialogue_key = dialogue.key()
        assert dialogue_key in self.dialogues
        self.dialogues.pop(dialogue_key)

    def on_error(self, operation: agent_pb2.Server.AgentMessage.Error.Operation,
                 dialogue_id: int,
                 message_id: int):
        raise NotImplementedError

    @abstractmethod
    def on_new_cfp(self):
        pass

    @abstractmethod
    def on_new_message(self):
        pass

    @abstractmethod
    def on_connection_error(self):
        pass

    def on_message(self, origin: str,
                   dialogue_id: int,
                   content: bytes):
        dialogue = self._get_dialogue((origin, dialogue_id))
        dialogue.on_message(origin, dialogue_id, content)

    def on_cfp(self, origin: str,
               dialogue_id: int,
               msg_id: int,
               target: int,
               query: CFP_TYPES):
        dialogue = self._get_dialogue((origin, dialogue_id))
        dialogue.on_cfp(origin, dialogue_id, msg_id, target, query)

    def on_propose(self, origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int,
                   proposal: PROPOSE_TYPES):
        dialogue = self._get_dialogue((origin, dialogue_id))
        dialogue.on_propose(origin, dialogue_id, msg_id, target, proposal)

    def on_accept(self, origin: str,
                  dialogue_id: int,
                  msg_id: int,
                  target: int, ):
        dialogue = self._get_dialogue((origin, dialogue_id))
        dialogue.on_accept(origin, dialogue_id, msg_id, target)

    def on_decline(self, origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int, ):
        dialogue = self._get_dialogue((origin, dialogue_id))
        dialogue.on_decline(origin, dialogue_id, msg_id, target)

    def _get_dialogue(self, key: DialogueKey) -> SingleDialogue:
        try:
            return self.dialogues[key]
        except KeyError:
            raise KeyError("Dialogue key {} not found.".format(key))


class GroupDialogues:

    def __init__(self,
                 agent: DialogueAgent):
        self.agent = agent
        self.dialogues = {}  # type: Dict[str, SingleDialogue]
        self.best_agent = None  # type: Optional[str]
        self.best_price = 0
        self.nb_answers = 0
        self.first = True

    def add_agents(self, agents: List[SingleDialogue]) -> None:
        for a in agents:
            self.dialogues[a.destination] = a
            self.agent.register_dialogue(a)

    @abstractmethod
    def better(self, price1: int, price2: int) -> bool:
        """"""

    def update(self, agent: str, price: int) -> None:
        self.nb_answers += 1
        if self.first:
            self.first = False
            self.best_price = price
            self.best_agent = agent
        elif self.better(price, self.best_price):
            self.best_price = price
            self.best_agent = agent
        else:
            pass

        if self.nb_answers >= len(self.dialogues):
            self.finished()

    @abstractmethod
    def finished(self):
        """"""

