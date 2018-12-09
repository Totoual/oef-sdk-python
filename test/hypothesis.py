# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
"""This module contains Hypothesis strategies for some of the package data types
(e.g. AttributeSchema, DataModel, Description, ...)"""


import typing
from typing import List

import hypothesis
from hypothesis.strategies import sampled_from, from_type, composite, text, booleans, one_of, none, lists

from oef.schema import ATTRIBUTE_TYPES, AttributeSchema, DataModel, Description


def _is_attribute_type(t: typing.Type):
    return t == bool or t in ATTRIBUTE_TYPES.__args__


attribute_schema_types = sampled_from(ATTRIBUTE_TYPES.__args__ + (bool,))
not_attribute_schema_types = from_type(type).filter(lambda t: not _is_attribute_type(t))


@composite
def _value_type_pairs(draw, type_strategy):
    type_ = draw(type_strategy)
    value = draw(from_type(type_))
    return value, type_


@composite
def attributes_schema(draw):
    attr_name = draw(text())
    attr_type = draw(attribute_schema_types)
    attr_required = draw(booleans())
    attr_description = draw(text())

    return AttributeSchema(attr_name, attr_type, attr_required, attr_description)


@composite
def data_models(draw):
    data_model_name = draw(text())
    data_model_description = draw(one_of(none(), text()))
    attributes = draw(lists(attributes_schema()))

    data_model = DataModel(data_model_name, attributes, data_model_description)
    return data_model


@composite
def schema_instances(draw, attributes: List[AttributeSchema]):
    if len(attributes) == 0:
        return {}
    else:
        keys, types, required_flags = zip(*[(a.name, a.type, a.required) for a in attributes])
        values = [draw(from_type(type_)) for type_ in types]
        return {k: v for k, v, r in zip(keys, values, required_flags) if r or draw(booleans())}


@composite
def descriptions(draw, from_data_model=False):
    if from_data_model:
        data_model = draw(data_models())
        attributes = data_model.attribute_schemas
    else:
        data_model = None
        attributes = draw(lists(attributes_schema()))
    attributes_values = draw(schema_instances(attributes))

    d = Description(attributes_values, data_model)
    return d


hypothesis.strategies.register_type_strategy(AttributeSchema, attributes_schema)
hypothesis.strategies.register_type_strategy(DataModel, data_models)
hypothesis.strategies.register_type_strategy(Description, descriptions)