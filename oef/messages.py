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

    def __init__(self, *args, **kwargs):
        self.msg = self._build_msg(*args, **kwargs)

    @abstractmethod
    def _build_msg(self, *args, **kwargs) -> agent_pb2.Agent.Message:
        raise NotImplementedError

    def to_envelope(self) -> agent_pb2.Envelope:
        envelope = agent_pb2.Envelope()
        envelope.send_message.CopyFrom(self.msg)
        return envelope


class AgentMessage(Message):
    pass


class SimpleMessage(Message):

    def _build_msg(self,
                   dialogue_id: int,
                   destination: str,
                   msg: bytes):
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = dialogue_id
        agent_msg.destination = destination
        agent_msg.content = msg
        return agent_msg


class CFP(Message):

    def _build_msg(self,
                   dialogue_id: int,
                   destination: str,
                   query: CFP_TYPES,
                   msg_id: Optional[int] = 1,
                   target: Optional[int] = 0) -> agent_pb2.Agent.Message:

        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = msg_id
        fipa_msg.target = target
        cfp = fipa_pb2.Fipa.Cfp()

        if query is None:
            cfp.nothing.CopyFrom(fipa_pb2.Fipa.Cfp.Nothing())
        elif isinstance(query, Query):
            cfp.query.CopyFrom(query.to_pb())
        elif isinstance(query, bytes):
            cfp.content = query
        fipa_msg.cfp.CopyFrom(cfp)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = dialogue_id
        agent_msg.destination = destination
        agent_msg.fipa.CopyFrom(fipa_msg)

        return agent_msg


class Propose(Message):

    def _build_msg(self,
                   dialogue_id: int,
                   destination: str,
                   proposals: PROPOSE_TYPES,
                   msg_id: int,
                   target: Optional[int] = None) -> agent_pb2.Agent.Message:

        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = msg_id
        fipa_msg.target = target if target is not None else (msg_id - 1)
        propose = fipa_pb2.Fipa.Propose()
        if isinstance(proposals, bytes):
            propose.content = proposals
        else:
            proposals_pb = fipa_pb2.Fipa.Propose.Proposals()
            proposals_pb.objects.extend([propose.as_instance() for propose in proposals])
            propose.proposals.CopyFrom(proposals_pb)
        fipa_msg.propose.CopyFrom(propose)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = dialogue_id
        agent_msg.destination = destination
        agent_msg.fipa.CopyFrom(fipa_msg)

        return agent_msg


class Accept(Message):

    def _build_msg(self,
                   dialogue_id: int,
                   destination: str,
                   msg_id: int,
                   target: Optional[int] = None):
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = msg_id
        fipa_msg.target = target if target is not None else (msg_id - 1)
        accept = fipa_pb2.Fipa.Accept()
        fipa_msg.accept.CopyFrom(accept)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = dialogue_id
        agent_msg.destination = destination
        agent_msg.fipa.CopyFrom(fipa_msg)

        return agent_msg


class Decline(Message):

    def _build_msg(self,
                   dialogue_id: int,
                   destination: str,
                   msg_id: int,
                   target: Optional[int] = None):
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = msg_id
        fipa_msg.target = target if target is not None else (msg_id - 1)
        decline = fipa_pb2.Fipa.Decline()
        fipa_msg.decline.CopyFrom(decline)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.dialogue_id = dialogue_id
        agent_msg.destination = destination
        agent_msg.fipa.CopyFrom(fipa_msg)

        return agent_msg

