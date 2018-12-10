# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
from abc import ABC, abstractmethod
from typing import Dict, Tuple

from oef import agent_pb2
from oef.agents import Agent
from oef.core import DialogueInterface, OEFProxy

DialogueAgent = None


class SingleDialogue(DialogueInterface, ABC):

    def __init__(self, agent: DialogueAgent,
                 destination: str,
                 dialogue_id: int,
                 is_buyer: bool):
        self.agent = agent
        self.destination = destination
        self.dialogue_id = dialogue_id
        self.is_buyer = is_buyer

    @abstractmethod
    def on_error(self):
        raise NotImplementedError


class DialogueAgent(Agent, ABC):

    def __init__(self, oef_proxy: OEFProxy):
        super().__init__(oef_proxy)
        self.dialogues = {}  # type: Dict[Tuple[str, int], SingleDialogue]

    def register_dialogue(self):
        pass

    def unregister_dialogue(self):
        pass

    def on_error(self, operation: agent_pb2.Server.AgentMessage.Error.Operation,
                 dialogue_id: int,
                 message_id: int):
        pass

    @abstractmethod
    def on_new_cfp(self):
        pass

    @abstractmethod
    def on_new_message(self):
        pass

    @abstractmethod
    def on_connection_error(self):
        pass

