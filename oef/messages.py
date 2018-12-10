# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
from abc import ABC, abstractmethod
from typing import Optional, Union, List

from oef.schema import Description

from oef import agent_pb2, fipa_pb2
from oef.query import Query

NoneType = type(None)
CFP_TYPES = Union[Query, bytes, NoneType]
PROPOSE_TYPES = Union[bytes, List[Description]]


class Message(ABC):

    @abstractmethod
    def to_envelope(self) -> agent_pb2.Envelope:
        raise NotImplementedError


class RegisterDescription(Message):

    def __init__(self, agent_description: Description):
        self.agent_description = agent_description

    def to_envelope(self) -> agent_pb2.Envelope:
        envelope = agent_pb2.Envelope()
        envelope.register_description.CopyFrom(self.agent_description.to_pb())
        return envelope


class RegisterService(Message):

    def __init__(self, service_description: Description):
        self.service_description = service_description

    def to_envelope(self) -> agent_pb2.Envelope:
        envelope = agent_pb2.Envelope()
        envelope.register_service.CopyFrom(self.service_description.to_pb())
        return envelope


class UnregisterDescription(Message):

    def __init__(self):
        pass

    def to_envelope(self) -> agent_pb2.Envelope:
        envelope = agent_pb2.Envelope()
        envelope.unregister_description.CopyFrom(agent_pb2.Envelope.Nothing())
        return envelope


class UnregisterService(Message):

    def __init__(self, service_description):
        self.service_description = service_description

    def to_envelope(self) -> agent_pb2.Envelope:
        envelope = agent_pb2.Envelope()
        envelope.unregister_service.CopyFrom(self.service_description.to_pb())
        return envelope


class SearchAgents(Message):
    def __init__(self, search_id: int, query: Query):
        self.search_id = search_id
        self.query = query

    def to_envelope(self):
        envelope = agent_pb2.Envelope()
        envelope.search_agents.query.CopyFrom(self.query.to_pb())
        envelope.search_agents.search_id = self.search_id
        return envelope


class SearchServices(Message):

    def __init__(self, search_id: int, query: Query):
        self.search_id = search_id
        self.query = query

    def to_envelope(self) -> agent_pb2.Envelope:
        envelope = agent_pb2.Envelope()
        envelope.search_services.query.CopyFrom(self.query.to_pb())
        envelope.search_services.search_id = self.search_id
        return envelope


class AgentMessage(Message, ABC):
    pass


class SimpleMessage(AgentMessage):

    def __init__(self,
                 dialogue_id: int,
                 destination: str,
                 msg: bytes):
        self.dialogue_id = dialogue_id
        self.destination = destination
        self.msg = msg

    def to_envelope(self):
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = self.dialogue_id
        agent_msg.destination = self.destination
        agent_msg.content = self.msg

        envelope = agent_pb2.Envelope()
        envelope.send_message.CopyFrom(agent_msg)
        return envelope


class CFP(AgentMessage):

    def __init__(self,
                 dialogue_id: int,
                 destination: str,
                 query: CFP_TYPES,
                 msg_id: Optional[int] = 1,
                 target: Optional[int] = 0):
        self.dialogue_id = dialogue_id
        self.destination = destination
        self.query = query
        self.msg_id = msg_id
        self.target = target

    def to_envelope(self) -> agent_pb2.Agent.Message:
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = self.msg_id
        fipa_msg.target = self.target
        cfp = fipa_pb2.Fipa.Cfp()

        if self.query is None:
            cfp.nothing.CopyFrom(fipa_pb2.Fipa.Cfp.Nothing())
        elif isinstance(self.query, Query):
            cfp.query.CopyFrom(self.query.to_pb())
        elif isinstance(self.query, bytes):
            cfp.content = self.query
        fipa_msg.cfp.CopyFrom(cfp)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = self.dialogue_id
        agent_msg.destination = self.destination
        agent_msg.fipa.CopyFrom(fipa_msg)

        envelope = agent_pb2.Envelope()
        envelope.send_message.CopyFrom(agent_msg)
        return envelope


class Propose(AgentMessage):

    def __init__(self,
                 dialogue_id: int,
                 destination: str,
                 proposals: PROPOSE_TYPES,
                 msg_id: int,
                 target: Optional[int] = None):
        self.dialogue_id = dialogue_id
        self.destination = destination
        self.proposals = proposals
        self.msg_id = msg_id
        self.target = target

    def to_envelope(self) -> agent_pb2.Agent.Message:
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = self.msg_id
        fipa_msg.target = self.target if self.target is not None else (self.msg_id - 1)
        propose = fipa_pb2.Fipa.Propose()
        if isinstance(self.proposals, bytes):
            propose.content = self.proposals
        else:
            proposals_pb = fipa_pb2.Fipa.Propose.Proposals()
            proposals_pb.objects.extend([propose.as_instance() for propose in self.proposals])
            propose.proposals.CopyFrom(proposals_pb)
        fipa_msg.propose.CopyFrom(propose)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = self.dialogue_id
        agent_msg.destination = self.destination
        agent_msg.fipa.CopyFrom(fipa_msg)

        envelope = agent_pb2.Envelope()
        envelope.send_message.CopyFrom(agent_msg)
        return envelope


class Accept(AgentMessage):

    def __init__(self,
                 dialogue_id: int,
                 destination: str,
                 msg_id: int,
                 target: Optional[int] = None):

        self.dialogue_id = dialogue_id
        self.destination = destination
        self.msg_id = msg_id
        self.target = target

    def to_envelope(self) -> agent_pb2.Agent.Message:
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = self.msg_id
        fipa_msg.target = self.target if self.target is not None else (self.msg_id - 1)
        accept = fipa_pb2.Fipa.Accept()
        fipa_msg.accept.CopyFrom(accept)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = self.dialogue_id
        agent_msg.destination = self.destination
        agent_msg.fipa.CopyFrom(fipa_msg)

        envelope = agent_pb2.Envelope()
        envelope.send_message.CopyFrom(agent_msg)
        return envelope


class Decline(AgentMessage):

    def __init__(self,
                 dialogue_id: int,
                 destination: str,
                 msg_id: int,
                 target: Optional[int] = None):

        self.dialogue_id = dialogue_id
        self.destination = destination
        self.msg_id = msg_id
        self.target = target

    def to_envelope(self):
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = self.msg_id
        fipa_msg.target = self.target if self.target is not None else (self.msg_id - 1)
        decline = fipa_pb2.Fipa.Decline()
        fipa_msg.decline.CopyFrom(decline)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = self.dialogue_id
        agent_msg.destination = self.destination
        agent_msg.fipa.CopyFrom(fipa_msg)

        envelope = agent_pb2.Envelope()
        envelope.send_message.CopyFrom(agent_msg)
        return envelope
