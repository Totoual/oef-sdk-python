# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Tom Nicholson <tom.nicholson@fetch.ai>

"""
Python bindings for OEFCore
"""

import asyncio
import copy
from typing import List, Callable, Optional, Union, Dict, Awaitable, Tuple

ATTRIBUTE_TYPES = Union[float, str, bool, int]
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


class AttributeInconsistencyException(Exception):
    """
    Raised when the attributes in a Description are inconsistent.

    Inconsistency is defined when values do not meet their respective schema, or if the values
    are not of an allowed type.
    """
    pass


def generate_schema(attribute_values):
    """
    Will generate a schema that matches the values stored in this description.

    For each attribute (name, value), we generate an AttributeSchema:
        AttributeInconsistencyException(name, type(value), false, "")
    Note that it is assumed that each attribute is not required.
    """
    return [AttributeSchema(k, type(v), False, "") for k, v in attribute_values.items()]


class Description(object):
    """
    Description of either a service or an agent so it can be understood by the OEF/ other agents.

    Contains values of the description, and an optional schema for checking format of values.

    Whenever the description is changed (including when it is create), the attribute values will
    checked to make sure they do not violate the attribute schema.
    """
    def __init__(self,
                 attribute_values: Dict[str, ATTRIBUTE_TYPES],
                 attribute_schemas: Optional[List[AttributeSchema]]) -> None:
        """
        :param attribute_values: the values of each attribute in the description. This is a
        dictionary from attribute name to attribute value, each attribute value must have a type
        in ATTRIBUTE_TYPES.
        :param attribute_schemas: optional schema of this description. If none is provided
        then the attribute values will not be checked against a schema. Schemas are extremely useful
        for preventing hard to debug problems, and are highly recommended.
        """
        self._values = copy.deepcopy(attribute_values)
        if attribute_schemas is not None:
            self._schemas = copy.deepcopy(attribute_schemas)
        else:
            self._schemas = generate_schema(self._values)

        self._check_consistency()

    def _check_consistency(self):
        """
        Checks the consistency of the values of this description.

        If an attribute_schemas has been provided, values are checked against that. If no attribute
        schema has been provided then minimal checking is performed based on the values in the
        provided attribute_value dictionary.
        :raises AttributeInconsistencyException: if values do not meet the schema, or if no schema
        is present if they have disallowed types.
        """
        if self._schemas is not None:
            # check that all required attributes in the schema are contained in
            required_attributes = [s.name for s in self._schemas if s.required]
            if not all(a in self._values for a in required_attributes):
                raise AttributeInconsistencyException("Missing required attribute.")

            # check that all values are defined in the schema
            all_schema_attributes = [s.name for s in self._schemas]
            if not all(k in all_schema_attributes for k in self._values):
                raise AttributeInconsistencyException("Have extra attribute not in schema")

            # check that each of the values are consistent with that specified in the schema
            for schema in self._schemas:
                if schema.name in self._values:
                    if not isinstance(self._values[schema.name], schema.type):
                        # values does not match type in schema
                        raise AttributeInconsistencyException(
                            "Attribute {} has incorrect type".format(schema.name))
                    elif not isinstance(self._values[schema.name], ATTRIBUTE_TYPES.__args__):
                        # value type matches schema, but it is not an allowed type
                        raise AttributeInconsistencyException(
                            "Attribute {} has unallowed type".format(schema.name))


class Query(object):
    """
    Representation of a search that is to be performed. Currently a search is represented as a
    set of key value pairs that must be contained in the description of the service/ agent.
    """
    pass

class Conversation(object):
    """
    A conversation
    """


class OEFProxy(object):
    """
    Proxy to the functionality of the OEF. Provides functionality for an agent to:
     * Register a description of itself
     * Register its services
     * Locate other agents
     * Locate other services
     * Establish a connection with another agent
    """

    def __init__(self, host_path: str) -> None:
        """
        :param host_path: the path to the host
        """
        self._host_path = host_path

        # these are setup in _connect_to_server
        self._server_reader = None
        self._server_writer = None

    async def _connect_to_server(self) -> Awaitable[Tuple[asyncio.StreamReader, asyncio.StreamWriter]]:
        return await asyncio.open_connection(self._host_path, OEF_SERVER_PORT)

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

    def register_service(self, service_description: Description) -> bool:
        """
        Adds a description of the respective service so that it can be understood/ queried by
        other agents in the OEF.
        :param service_description: description of the services to add
        :returns: `True` if service is successfully added, `False` otherwise. Can fail if such an
        service already exists in the OEF.
        """
        pass

    def unregister_service(self, service_description: Description) -> bool:
        """
        Adds a description of the respective service so that it can be understood/ queried by
        other agents in the OEF.
        :param service_description: description of the services to add
        :returns: `True` if service is successfully added, `False` otherwise. Can fail if such an
        service already exists in the OEF.
        """
        pass

    def search_agents(self, query: Query) -> List[Description]:
        """
        Allows an agent to search for other agents it is interested in communicating with. This can
        be useful when an agent wishes to directly proposition the provision of a service that it
        thinks another agent may wish to be able to offer it. All matching agents are returned
        (potentially including ourself)
        :param query: specifications of the constraints on the agents that are matched
        :returns: a list of the matching agents
        """
        pass

    def search_services(self, query: Query) -> List[Description]:
        """
        Allows an agent to search for a particular service. This allows constrained search of all
        services that have been registered with the OEF. All matching services will be returned
        (potentially including services offered by ourself)
        :param query: the constraint on the matching services
        """
        pass

    def start_conversation(self, agent_id: str) -> Conversation:
        """
        Start a conversation with the specified agent. This allows a direct channel of communication
        with an agent.
        """
        pass
