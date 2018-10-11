# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Tom Nicholson <tom.nicholson@fetch.ai>

"""
Python bindings for OEFCore
"""

import asyncio
import copy
import agent_pb2 as agent_pb2
import query_pb2 as query_pb2
import fipa_pb2 as fipa_pb2
import struct

from typing import List, Callable, Optional, Union, Dict, Awaitable, Tuple

ATTRIBUTE_TYPES = Union[float, str, bool, int]

def attribute_type_to_pb(attribute_type: ATTRIBUTE_TYPES):
    if attribute_type == bool:
        return query_pb2.Query.Attribute.BOOL
    elif attribute_type == int:
        return query_pb2.Query.Attribute.INT
    elif attribute_type == float:
        return query_pb2.Query.Attribute.FLOAT
    elif attribute_type == str:
        return query_pb2.Query.Attribute.STRING

def attribute_pb_to_type(attribute_type : query_pb2.Query.Attribute):
    if attribute_type == query_pb2.Query.Attribute.BOOL:
        return bool
    elif attribute_type == query_pb2.Query.Attribute.STRING :
        return str
    elif attribute_type == query_pb2.Query.Attribute.INT :
        return int
    elif attribute_type == query_pb2.Query.Attribute.FLOAT :
        return float
    
"""
The allowable types that an Attribute can have
"""

OEF_SERVER_PORT = 3333
"""
The port the OEF server is going to be listening on
"""

class AttributeSchema(object):
    """
    Description of a single element of datum of either a description or a service.

    This defines the schema that a single entry in a schema must take.
    """
    def __init__(self,
                 attribute_name: str,
                 attribute_type: ATTRIBUTE_TYPES,
                 is_attribute_required: bool,
                 attribute_description: Optional[str] = None) -> None:
        """
        :param attribute_name: the name of this attribute
        :param attribute_type: the type of this attribute, must be a type in ATTRIBUTE_TYPES
        :param is_attribute_required: does this attribute have to be included
        :param attribute_description: optional description of this attribute
        """
        self.name = attribute_name
        self.type = attribute_type
        self.required = is_attribute_required
        self.description = attribute_description or ""

    def __eq__(self, other):
        if isinstance(other, AttributeSchema):
            return (self.name == other.name and self.type == other.type and
                    self.required == other.required and self.description == other.description)
        return False

    def to_pb(self):
        attribute = query_pb2.Query.Attribute()
        attribute.name = self.name
        attribute.type = attribute_type_to_pb(self.type)
        attribute.required = self.required
        if self.description is not None:
            attribute.description = self.description
        return attribute

    @classmethod
    def from_pb(cls, attribute : query_pb2.Query.Attribute):
        return cls(attribute.name, attribute_pb_to_type(attribute.type), attribute.required, attribute.description)

class AttributeInconsistencyException(Exception):
    """
    Raised when the attributes in a Description are inconsistent.

    Inconsistency is defined when values do not meet their respective schema, or if the values
    are not of an allowed type.
    """
    pass



class DataModel(object):
    def __init__(self,
                 name : str,
                 attribute_schemas: List[AttributeSchema],
                 description : Optional[str] = None) -> None:
        self.name = name
        self.attribute_schemas = copy.deepcopy(attribute_schemas) # what for ?
        self.description = description

    @classmethod
    def from_pb(cls, model : query_pb2.Query.DataModel):
        name = model.name
        attributes = [AttributeSchema.from_pb(attr_pb) for attr_pb in model.attributes]
        description = model.description
        return cls(name, attributes, description)
        
    def to_pb(self):
        model = query_pb2.Query.DataModel()
        model.name = self.name
        model.attributes.extend([attr.to_pb() for attr in self.attribute_schemas])
        if self.description is not None:
            model.description = self.description
        return model

def generate_schema(model_name, attribute_values):
    """
    Will generate a schema that matches the values stored in this description.

    For each attribute (name, value), we generate an AttributeSchema:
        AttributeInconsistencyException(name, type(value), false, "")
    Note that it is assumed that each attribute is required.
    """
    return DataModel(model_name, [AttributeSchema(k, type(v), True, "") for k, v in attribute_values.items()])


def extract_value(value : query_pb2.Query.Value) -> ATTRIBUTE_TYPES:
    value_case = value.WhichOneof("value")
    if value_case == "s":
        return value.s
    elif value_case == "b":
        return value.b
    elif value_case == "i":
        return value.i
    elif value_case == "f":
        return value.f

class Description(object):
    """
    Description of either a service or an agent so it can be understood by the OEF/ other agents.

    Contains values of the description, and an optional schema for checking format of values.

    Whenever the description is changed (including when it is create), the attribute values will
    checked to make sure they do not violate the attribute schema.
    """
    def __init__(self,
                 attribute_values: Dict[str, ATTRIBUTE_TYPES],
                 data_model: DataModel) -> None:
        """
        :param attribute_values: the values of each attribute in the description. This is a
        dictionary from attribute name to attribute value, each attribute value must have a type
        in ATTRIBUTE_TYPES.
        :param attribute_schemas: optional schema of this description. If none is provided
        then the attribute values will not be checked against a schema. Schemas are extremely useful
        for preventing hard to debug problems, and are highly recommended.
        """
        self._values = copy.deepcopy(attribute_values)
        self._data_model = data_model
        self._check_consistency()

    @classmethod
    def from_pb(cls, query_instance : query_pb2.Query.Instance):
        model = DataModel.from_pb(query_instance.model)
        values = dict([(attr.key,extract_value(attr.value)) for attr in query_instance.values])
        return cls(values, model)
        
    def _to_key_value_pb(self, key: str, value: ATTRIBUTE_TYPES):
        kv = query_pb2.Query.KeyValue()
        kv.key = key
        if isinstance(value, bool):
            kv.value.b = value
        elif isinstance(value, int):
            kv.value.i = value
        elif isinstance(value, float):
            kv.value.f = value
        elif isinstance(value, str):
            kv.value.s = value
        return kv

    def as_instance(self):
        instance = query_pb2.Query.Instance()
        instance.model.CopyFrom(self._data_model.to_pb())
        instance.values.extend([self._to_key_value_pb(key, value) for key, value in self._values.items()])
        return instance
    
    def to_pb(self):
        description = agent_pb2.AgentDescription()
        description.description.CopyFrom(self.as_instance())
        return description
        
    def _check_consistency(self):
        """
        Checks the consistency of the values of this description.

        If an attribute_schemas has been provided, values are checked against that. If no attribute
        schema has been provided then minimal checking is performed based on the values in the
        provided attribute_value dictionary.
        :raises AttributeInconsistencyException: if values do not meet the schema, or if no schema
        is present if they have disallowed types.
        """
        if self._data_model is not None:
            # check that all required attributes in the schema are contained in
            required_attributes = [s.name for s in self._data_model.attribute_schemas if s.required]
            if not all(a in self._values for a in required_attributes):
                raise AttributeInconsistencyException("Missing required attribute.")

            # check that all values are defined in the schema
            all_schema_attributes = [s.name for s in self._data_model.attribute_schemas]
            if not all(k in all_schema_attributes for k in self._values):
                raise AttributeInconsistencyException("Have extra attribute not in schema")

            # check that each of the values are consistent with that specified in the schema
            for schema in self._data_model.attribute_schemas:
                if schema.name in self._values:
                    if not isinstance(self._values[schema.name], schema.type):
                        # values does not match type in schema
                        raise AttributeInconsistencyException(
                            "Attribute {} has incorrect type".format(schema.name))
                    elif not isinstance(self._values[schema.name], ATTRIBUTE_TYPES.__args__):
                        # value type matches schema, but it is not an allowed type
                        raise AttributeInconsistencyException(
                            "Attribute {} has unallowed type".format(schema.name))


# there must be a better way ...
class Relation(object):
    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        self.value = value

    def to_pb(self):
        relation = query_pb2.Query.Relation()
        relation.op = self._to_pb()
        query_value = query_pb2.Query.Value()
        if isinstance(self.value, bool):
            query_value.b = self.value
        elif isinstance(self.value, int):
            query_value.i = self.value
        elif isinstance(self.value, float):
            query_value.f = self.value
        elif isinstance(self.value, str):
            query_value.s = self.value
        relation.val.CopyFrom(query_value)
        return relation


class Eq(Relation):
    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        super().__init__(value)
    def _to_pb(self):
        return query_pb2.Query.Relation.EQ
    
class NotEq(Relation):
    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        super().__init__(value)
    def _to_pb(self):
        return query_pb2.Query.Relation.NOTEQ
    
class Lt(Relation):
    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        super().__init__(value)
    def _to_pb(self):
        return query_pb2.Query.Relation.LT
    
class LtEq(Relation):
    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        super().__init__(value)
    def _to_pb(self):
        return query_pb2.Query.Relation.LTEQ
    
class Gt(Relation):
    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        super().__init__(value)
    def _to_pb(self):
        return query_pb2.Query.Relation.GT
    
class GtEq(Relation):
    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        super().__init__(value)
    def _to_pb(self):
        return query_pb2.Query.Relation.GTEQ

def relation_from_pb(relation : query_pb2.Query.Relation) -> Relation:
    relations_from_pb = {query_pb2.Query.Relation.GTEQ: GtEq, query_pb2.Query.Relation.GT: Gt,
                         query_pb2.Query.Relation.LTEQ: LtEq, query_pb2.Query.Relation.LT: Lt,
                         query_pb2.Query.Relation.NOTEQ: NotEq, query_pb2.Query.Relation.EQ: Eq}
    value_case = relation.val.WhichOneof("value")
    if value_case == "s":
        return relations_from_pb[relation.op](relation.val.s)
    elif value_case == "b":
        return relations_from_pb[relation.op](relation.val.b)
    elif value_case == "i":
        return relations_from_pb[relation.op](relation.val.i)
    elif value_case == "f":
        return relations_from_pb[relation.op](relation.val.f)
        
    
RANGE_TYPES = Union[Tuple[str,str],Tuple[int,int],Tuple[float,float]]

class Range(object):
    def __init__(self, values: RANGE_TYPES) -> None:
        self._values = values

    def to_pb(self):
        range_ = query_pb2.Query.Range()
        if isinstance(self._values[0], str):
            values = query_pb2.Query.StringPair()
            values.first = self._values[0]
            values.second = self._values[1]
            range_.s.CopyFrom(values)
        elif isinstance(self._values[0], int):
            values = query_pb2.Query.IntPair()
            values.first = self._values[0]
            values.second = self._values[1]
            range_.i.CopyFrom(values)
        elif isinstance(self._values[0], float):
            values = query_pb2.Query.FloatPair()
            values.first = self._values[0]
            values.second = self._values[1]
            range_.f.CopyFrom(values)
        return range_
            
CONSTRAINT_TYPES = Union[Relation,Range]

class Constraint(object):
    def __init__(self,
                 attribute: AttributeSchema,
                 constraint: CONSTRAINT_TYPES) -> None:
        self._attribute = attribute
        self._constraint = constraint
        
    def to_pb(self):
        constraint_type = query_pb2.Query.Constraint.ConstraintType()
        if isinstance(self._constraint, Relation):
            constraint_type.relation.CopyFrom(self._constraint.to_pb())
        elif isinstance(self._constraint, Range):
            constraint_type.range_.CopyFrom(self._constraint.to_pb())
        constraint = query_pb2.Query.Constraint()
        constraint.attribute.CopyFrom(self._attribute.to_pb())
        constraint.constraint.CopyFrom(constraint_type)
        return constraint

    @classmethod
    def from_pb(cls, constraint_pb : query_pb2.Query.Constraint):
        constraint_case = constraint_pb.constraint.WhichOneof("constraint")
        if constraint_case == "relation":
            constraint = relation_from_pb(constraint_pb.constraint.relation)
        return cls(AttributeSchema.from_pb(constraint_pb.attribute), constraint)
    
class Query(object):
    """
    Representation of a search that is to be performed. Currently a search is represented as a
    set of key value pairs that must be contained in the description of the service/ agent.
    """
    def __init__(self,
                 constraints: List[Constraint],
                 model: Optional[DataModel] = None) -> None:
        self._constraints = constraints
        self._model = model

    def to_query_pb(self):
        query = query_pb2.Query.Model()
        query.constraints.extend([constraint.to_pb() for constraint in self._constraints])
        if self._model is not None:
            query.model.CopyFrom(self._model.to_pb())
        return query

    def to_pb(self):
        query = self.to_query_pb()
        agent_search = agent_pb2.AgentSearch()
        agent_search.query.CopyFrom(query)
        return agent_search

    @classmethod
    def from_pb(cls, query : query_pb2.Query.Model):
        constraints = [Constraint.from_pb(constraint_pb) for constraint_pb in query.constraints]
        return cls(constraints, DataModel.from_pb(query.model) if query.HasField("model") else None)

class Conversation(object):
    """
    A conversation
    """

NoneType = type(None)
CFP_TYPES = Union[Query,bytes,NoneType]
PROPOSE_TYPES = Union[bytes,List[Description]]

class OEFProxy(object):
    """
    Proxy to the functionality of the OEF. Provides functionality for an agent to:
     * Register a description of itself
     * Register its services
     * Locate other agents
     * Locate other services
     * Establish a connection with another agent
    """

    def __init__(self, public_key: str, host_path: str) -> None:
        """
        :param host_path: the path to the host
        """
        self._public_key = public_key
        self._host_path = host_path

        # these are setup in _connect_to_server
        self._connection = None
        self._server_reader = None
        self._server_writer = None

    async def _connect_to_server(self, event_loop) -> Awaitable[Tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
        return await asyncio.open_connection(self._host_path, OEF_SERVER_PORT, loop=event_loop)

    def _send(self, protobuf_msg): # async too ?
        serialized_msg = protobuf_msg.SerializeToString()
        nbytes = struct.pack("I", len(serialized_msg))
        self._server_writer.write(nbytes)
        self._server_writer.write(serialized_msg)

    async def _receive(self):
        nbytes_packed = await self._server_reader.read(len(struct.pack("I",0)))
        print("received ${0}".format(nbytes_packed))
        nbytes = struct.unpack("I", nbytes_packed)
        print("received unpacked ${0}".format(nbytes[0]))
        print("Preparing to receive ${0} bytes ...".format(nbytes[0]))
        return await self._server_reader.read(nbytes[0])

    async def connect(self) -> bool:
        event_loop = asyncio.get_event_loop()
        self._connection = await self._connect_to_server(event_loop)
        self._server_reader, self._server_writer = self._connection
        # Step 1: Agent --(ID)--> OEFCore
        pb_public_key = agent_pb2.Agent.Server.ID()
        pb_public_key.public_key = self._public_key
        self._send(pb_public_key)
        # Step 2: OEFCore --(Phrase)--> Agent
        data = await self._receive()
        pb_phrase = agent_pb2.Server.Phrase()
        pb_phrase.ParseFromString(data)
        case = pb_phrase.WhichOneof("payload")
        if case == "failure":
            return False
        # Step 3: Agent --(Answer)--> OEFCore
        pb_answer = agent_pb2.Agent.Server.Answer()
        pb_answer.answer = pb_phrase.phrase[::-1]
        self._send(pb_answer)
        # Step 4: OEFCore --(Connected)--> Agent
        data = await self._receive()
        pb_status = agent_pb2.Server.Connected()
        pb_status.ParseFromString(data)
        return pb_status.status

    async def loop(self, agent) -> None:
        while True:
            data = await self._receive()
            msg = agent_pb2.Server.AgentMessage()
            msg.ParseFromString(data)
            case = msg.WhichOneof("payload")
            print("loop {0}".format(case))
            if case == "agents":
                agent.onSearchResult(msg.agents.agents)
            elif case == "error":
                agent.onError(msg.error.operation, msg.error.conversation_id, msg.error.msgid)
            elif case == "content":
                content_case = msg.content.WhichOneof("payload")
                print("msg content {0}".format(content_case))
                if content_case == "content":
                    agent.onMessage(msg.content.origin, msg.content.conversation_id, msg.content.content)
                elif content_case == "fipa":
                    fipa = msg.content.fipa
                    fipa_case = fipa.WhichOneof("msg")
                    if fipa_case == "cfp":
                        cfp_case = fipa.cfp.WhichOneof("payload")
                        if cfp_case == "nothing":
                            query = None
                        elif cfp_case == "content":
                            query = fipa.cfp.content
                        elif cfp_case == "query":
                            query = Query.from_pb(fipa.cfp.query)
                        agent.onCFP(msg.content.origin, msg.content.conversation_id, fipa.msg_id, fipa.target, query)
                    elif fipa_case == "propose":
                        propose_case = fipa.propose.WhichOneof("payload")
                        if propose_case == "content":
                            proposals = fipa.propose.content
                        else:
                            proposals = [Description.from_pb(propose) for propose in fipa.propose.proposals.objects]
                        agent.onPropose(msg.content.origin, msg.content.conversation_id, fipa.msg_id, fipa.target, proposals)
                    elif fipa_case == "accept":
                        agent.onAccept(msg.content.origin, msg.content.conversation_id, fipa.msg_id, fipa.target)
                    elif fipa_case == "decline":
                        agent.onDecline(msg.content.origin, msg.content.conversation_id, fipa.msg_id, fipa.target)
                    else:
                        print("Not implemented yet: fipa {0}".format(fipa_case))
            

    def send_message(self, conversation_id : str, destination : str, msg : bytes):
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.conversation_id = conversation_id
        agent_msg.destination = destination
        agent_msg.content = msg
        envelope = agent_pb2.Envelope()
        envelope.message.CopyFrom(agent_msg)
        self._send(envelope)
        
    def send_cfp(self, conversation_id : str, destination : str, query : CFP_TYPES, msg_id : Optional[int] = 1,
                 target : Optional[int] = 0):
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = msg_id
        fipa_msg.target = target
        cfp = fipa_pb2.Fipa.Cfp()
        if query is None:
            cfp.nothing.CopyFrom(fipa_pb2.Fipa.Cfp.Nothing())
        elif isinstance(query, Query):
            cfp.query.CopyFrom(query.to_query_pb())
        elif isinstance(query, bytes):
            cfp.content = query
        fipa_msg.cfp.CopyFrom(cfp)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.conversation_id = conversation_id
        agent_msg.destination = destination
        agent_msg.fipa.CopyFrom(fipa_msg)
        envelope = agent_pb2.Envelope()
        envelope.message.CopyFrom(agent_msg)
        self._send(envelope)
        
    def send_propose(self, conversation_id : str, destination : str, proposals : PROPOSE_TYPES, msg_id : int,
                     target : Optional[int] = None):
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
        agent_msg.conversation_id = conversation_id
        agent_msg.destination = destination
        agent_msg.fipa.CopyFrom(fipa_msg)
        envelope = agent_pb2.Envelope()
        envelope.message.CopyFrom(agent_msg)
        print("propose envelope {0}".format(envelope))
        self._send(envelope)
        
    def send_accept(self, conversation_id : str, destination : str, msg_id : int,
                    target : Optional[int] = None):
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = msg_id
        fipa_msg.target = target if target is not None else (msg_id - 1)
        accept = fipa_pb2.Fipa.Accept()
        fipa_msg.accept.CopyFrom(accept)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.conversation_id = conversation_id
        agent_msg.destination = destination
        agent_msg.fipa.CopyFrom(fipa_msg)
        envelope = agent_pb2.Envelope()
        envelope.message.CopyFrom(agent_msg)
        print("accept envelope {0}".format(envelope))
        self._send(envelope)
        
    def send_decline(self, conversation_id : str, destination : str, msg_id : int,
                     target : Optional[int] = None):
        fipa_msg = fipa_pb2.Fipa.Message()
        fipa_msg.msg_id = msg_id
        fipa_msg.target = target if target is not None else (msg_id - 1)
        decline = fipa_pb2.Fipa.Decline()
        fipa_msg.accept.CopyFrom(decline)
        agent_msg = agent_pb2.Agent.Message()
        agent_msg.conversation_id = conversation_id
        agent_msg.destination = destination
        agent_msg.fipa.CopyFrom(fipa_msg)
        envelope = agent_pb2.Envelope()
        envelope.message.CopyFrom(agent_msg)
        print("decline envelope {0}".format(envelope))
        self._send(envelope)
        
    def close(self) -> None:
        """
        Used to tear down resources associated with this Proxy, i.e. the writing connection with
        the server.
        """
        self._server_writer.close()

    def register_agent(self, agent_description: Description) -> bool:
        """
        Adds a description of an agent to the OEF so that it can be understood/ queried by
        other agents in the OEF.

        :param agent_description: description of the agent to add
        :returns: `True` if agent is successfully added, `False` otherwise. Can fail if such an
        agent already exists in the OEF.
        """
        pass

    def unregister_agent(self,
                         agent_description: Description,
                         conversation_handler: Callable[[Conversation], None]) -> bool:
        """
        Removes the description of an agent from the OEF. This agent will no longer be queryable
        by other agents in the OEF. A conversation handler must be provided that allows the agent
        to receive and manage conversations from other agents wishing to communicate with it.

        :param agent_description: description of the agent to remove
        :param conversation_handler: function that allows handling of conversations with other
        agents
        :returns: `True` if agent is successfully removed, `False` otherwise. Can fail if
        such an agent is not registered with the OEF.
        """
        pass

    def register_service(self, service_description: Description):
        """
        Adds a description of the respective service so that it can be understood/ queried by
        other agents in the OEF.
        :param service_description: description of the services to add
        :returns: `True` if service is successfully added, `False` otherwise. Can fail if such an
        service already exists in the OEF.
        """
        envelope = agent_pb2.Envelope()
        envelope.register.CopyFrom(service_description.to_pb())
        self._send(envelope)

    def unregister_service(self, service_description: Description) -> None:
        """
        Adds a description of the respective service so that it can be understood/ queried by
        other agents in the OEF.
        :param service_description: description of the services to add
        :returns: `True` if service is successfully added, `False` otherwise. Can fail if such an
        service already exists in the OEF.
        """
        pass

    def search_agents(self, query: Query) -> None:
        """
        Allows an agent to search for other agents it is interested in communicating with. This can
        be useful when an agent wishes to directly proposition the provision of a service that it
        thinks another agent may wish to be able to offer it. All matching agents are returned
        (potentially including ourself)
        :param query: specifications of the constraints on the agents that are matched
        :returns: a list of the matching agents
        """
        pass

    def search_services(self, query: Query) -> None:
        """
        Allows an agent to search for a particular service. This allows constrained search of all
        services that have been registered with the OEF. All matching services will be returned
        (potentially including services offered by ourself)
        :param query: the constraint on the matching services
        """
        envelope = agent_pb2.Envelope()
        envelope.query.CopyFrom(query.to_pb())
        self._send(envelope)


    def start_conversation(self, agent_id: str) -> Conversation:
        """
        Start a conversation with the specified agent. This allows a direct channel of communication
        with an agent.
        """
        pass
