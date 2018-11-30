# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
from typing import List, Dict

import pytest

from oef.schema import AttributeSchema, ATTRIBUTE_TYPES, DataModel, AttributeInconsistencyException, Description, \
    generate_schema


def check_inconsistency_checker(schema: List[AttributeSchema], values: Dict[str, ATTRIBUTE_TYPES], exception_string):
    """
    Used to check that that AttributeInconsistencyException is raised with a certain string
    when the two inconsistent schema and values are used to build a Description
    """
    data_model = DataModel("foo", schema, "")
    with pytest.raises(AttributeInconsistencyException, match=exception_string):
        _ = Description(values, data_model)


def test_raise_when_not_required_attribute_is_ommitted():
    """
    Test that if we miss out a required attribute, we moan about it
    """
    check_inconsistency_checker([AttributeSchema("foo", float, True)], {}, "Missing required attribute.")


def test_raise_when_have_extra_attribute():
    """
    Test that if we have an attribute that is not in the schema, we moan about it
    """
    check_inconsistency_checker([], {"foo": "bar"}, "extra attribute")


def test_raise_when_have_incorrect_types():
    """
    Test that if an attribute value has a value inconsistent with its schema, we moan.
    """
    check_inconsistency_checker([AttributeSchema("foo", float, True)],
                                {"foo": "bar"},
                                "incorrect type")


def test_raise_when_have_unallowed_types():
    """
    Test that if an attribute value has a value inconsistent with its schema, we moan.
    """
    check_inconsistency_checker([AttributeSchema("foo", tuple, True)],
                                {"foo": tuple()},
                                "unallowed type")


def test_raise_when_disallowed_types():
    """
    Test that if an attribute has a type that is no in the allowed set, we moan
    """
    check_inconsistency_checker([], {"foo": tuple()}, "Have extra attribute not in schema")


def generate_schema_checker(values, expected_schema):
    """
    Used to check that generate_schema constructs the expected schema from the provided values
    """
    actual_schema = generate_schema("foo", values)

    assert actual_schema.attribute_schemas == expected_schema


def test_generate_schema_empty():
    """
    Test that construct_schema constructs the correct schema from empty attribute values
    """
    generate_schema_checker({}, [])


def test_generate_schema_single_element():
    """
    Test that construct_schema constructs the correct schema from single-element attribute
    values
    """
    generate_schema_checker({"foo":"bar"}, [AttributeSchema("foo", str, True, "")])


def test_generate_schema_longer_values():
    """
    Test that construct_schema constructs the correct schema from longer dict of values
    """
    values = {"foo": "bar",
              "number": 1234,
              "float": 123.4,
              "bool": True}
    schema = [AttributeSchema("foo", str, True, ""),
              AttributeSchema("number", int, True, ""),
              AttributeSchema("float", float, True, ""),
              AttributeSchema("bool", bool, True, "")]

    generate_schema_checker(values, schema)