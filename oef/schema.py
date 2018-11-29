# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import copy
from typing import Union, Type, Optional, List, Dict

import oef.agent_pb2 as agent_pb2
import oef.query_pb2 as query_pb2


"""
The allowable types that an Attribute can have
"""
ATTRIBUTE_TYPES = Union[float, str, bool, int]


def attribute_type_to_pb(attribute_type: Type[ATTRIBUTE_TYPES]):
    if attribute_type == bool:
        return query_pb2.Query.Attribute.BOOL
    elif attribute_type == int:
        return query_pb2.Query.Attribute.INT
    elif attribute_type == float:
        return query_pb2.Query.Attribute.FLOAT
    elif attribute_type == str:
        return query_pb2.Query.Attribute.STRING


def attribute_pb_to_type(attribute_type: query_pb2.Query.Attribute):
    if attribute_type == query_pb2.Query.Attribute.BOOL:
        return bool
    elif attribute_type == query_pb2.Query.Attribute.STRING:
        return str
    elif attribute_type == query_pb2.Query.Attribute.INT:
        return int
    elif attribute_type == query_pb2.Query.Attribute.FLOAT:
        return float


class AttributeSchema(object):
    """
    Description of a single element of datum of either a description or a service.

    This defines the schema that a single entry in a schema must take.
    """

    def __init__(self,
                 attribute_name: str,
                 attribute_type: Type[ATTRIBUTE_TYPES],
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
    def from_pb(cls, attribute: query_pb2.Query.Attribute):
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
                 name: str,
                 attribute_schemas: List[AttributeSchema],
                 description: Optional[str] = None) -> None:
        self.name = name
        self.attribute_schemas = copy.deepcopy(attribute_schemas)  # what for ?
        self.description = description

    @classmethod
    def from_pb(cls, model: query_pb2.Query.DataModel):
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

    def __eq__(self, other):
        if type(other) != DataModel:
            return False
        return self.name == other.name and \
            self.attribute_schemas == other.attribute_schema and \
            self.description == other.description


def generate_schema(model_name, attribute_values):
    """
    Will generate a schema that matches the values stored in this description.

    For each attribute (name, value), we generate an AttributeSchema:
        AttributeInconsistencyException(name, type(value), false, "")
    Note that it is assumed that each attribute is required.
    """
    return DataModel(model_name, [AttributeSchema(k, type(v), True, "") for k, v in attribute_values.items()])


def extract_value(value: query_pb2.Query.Value) -> ATTRIBUTE_TYPES:
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
                 data_model: DataModel = None) -> None:
        """
        :param attribute_values: the values of each attribute in the description. This is a
        dictionary from attribute name to attribute value, each attribute value must have a type
        in ATTRIBUTE_TYPES.
        :param attribute_schemas: optional schema of this description. If none is provided
        then the attribute values will not be checked against a schema. Schemas are extremely useful
        for preventing hard to debug problems, and are highly recommended.
        """
        self._values = copy.deepcopy(attribute_values)
        if data_model is not None:
            self._data_model = data_model
            self._check_consistency()
        else:
            # TODO: choose a default name for the data model
            self._data_model = generate_schema("", attribute_values)

    @classmethod
    def from_pb(cls, query_instance: query_pb2.Query.Instance):
        model = DataModel.from_pb(query_instance.model)
        values = dict([(attr.key, extract_value(attr.value)) for attr in query_instance.values])
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

