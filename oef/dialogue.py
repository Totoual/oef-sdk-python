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

"""

oef.dialogue
~~~~~~~~~~~~

This module contains classes to implement more complex dialogues.


"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Optional

from oef.messages import CFP_TYPES, PROPOSE_TYPES

from oef.agents import Agent
from oef.core import DialogueInterface, OEFProxy

import uuid

DialogueKey = Tuple[str, int]
DialogueAgent = None


class SingleDialogue(DialogueInterface, ABC):
    """
    This class is used to hold information about a dialogue with another agent.

    It implements the :class:`~oef.core.DialogueInterface`, so it is needed to implement all the message handlers
    (i.e. :func:`~oef.core.DialogueInerface.on_message`, :func:`~oef.core.DialogueInerface.on_cfp`...)
    """

    def __init__(self, agent: DialogueAgent,
                 destination: str,
                 id_: Optional[int] = None):
        """
        Initialize a single dialogue.

        :param agent: the agent who holds the dialogue.
        :param destination: the identifier of the agent participating in the dialogue
        :param id_: the identifier of this dialogue.
        """
        self.agent = agent
        self.destination = destination
        self.id = id_
        if id_:
            self.is_buyer = False
        else:
            self.id = uuid.uuid4().time_mid
            self.is_buyer = True

    @abstractmethod
    def on_error(self) -> None:
        """
        A callback that is called whenever an error occurs.

        :return: ``None``
        """

    @property
    def key(self) -> DialogueKey:
        """The identifier for this dialogue."""
        return self.destination, self.id


class DialogueAgent(Agent, ABC):
    """
    This class implements a special agent that uses the dialogue to make complex interactions with other agents.
    """

    def __init__(self, oef_proxy: OEFProxy):
        super().__init__(oef_proxy)
        self.dialogues = {}  # type: Dict[DialogueKey, SingleDialogue]

    def register_dialogue(self, dialogue: SingleDialogue) -> None:
        """
        Register a dialogue with another agent.

        :param dialogue: the dialogue to register in the state of the agent.
        :return: ``None``
        :raises ValueError: if the dialogue key is already present.
        """
        dialogue_key = dialogue.key
        if dialogue_key not in self.dialogues:
            raise ValueError("Dialogue key {} already in use.".format(dialogue_key))
        self.dialogues[dialogue_key] = dialogue

    def unregister_dialogue(self, dialogue: SingleDialogue) -> None:
        """
        Unregister a dialogue from the state of the agent.

        :param dialogue: the dialogue to unregister.
        :return: ``None``
        :raises ValueError
        """
        dialogue_key = dialogue.key
        if dialogue_key not in self.dialogues:
            raise ValueError("Dialogue key {} already in use.".format(dialogue_key))
        self.dialogues.pop(dialogue_key)

    @abstractmethod
    def on_new_cfp(self):
        """Handle a new CFP message."""

    @abstractmethod
    def on_new_message(self):
        """Handle a new :class:`~oef.messages.Message` message."""

    @abstractmethod
    def on_connection_error(self):
        """Handle a connection error."""

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
    """
    Class to handle a set of dialogues and take decisions taking into accounts all the dialogues.
    """

    def __init__(self,
                 agent: DialogueAgent):
        """
        Instantiate a group of dialogues.

        :param agent: the agent that hold the group of dialogues.
        """
        self.agent = agent
        self.dialogues = {}  # type: Dict[str, SingleDialogue]
        self.best_agent = None  # type: Optional[str]
        self.best_price = 0
        self.nb_answers = 0
        self.first = True

    def add_agents(self, agents: List[SingleDialogue]) -> None:
        """
        Add a list of dialogues to the group.

        :param agents: a list of dialogues.
        :return: ``None``
        """
        for a in agents:
            self.dialogues[a.destination] = a
            self.agent.register_dialogue(a)

    @abstractmethod
    def better(self, price1: int, price2: int) -> bool:
        """
        Determine whether a price is better than another one.

        :param price1: the first price to compare.
        :param price2: the second price to compare
        :return: ``True`` if the first price is better than the second, ``False`` otherwise.
        """

    def update(self, agent: str, price: int) -> None:
        """
        Update the price value received from another agent, e.g. during a negotiation.

        :param agent: the agent who sent us the price.
        :param price: the price sent by the other agent.
        :return: ``None``
        """
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
    def finished(self) -> None:
        """
        Handle the end of all the dialogues.

        :return: ``None``
        """

