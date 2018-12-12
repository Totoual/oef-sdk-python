# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.
from hypothesis import given

from oef import query_pb2
from oef.query import Relation, Range, Set, And, Or, Constraint, Query
from test.hypothesis.strategies import relations, ranges, query_sets, and_constraints, or_constraints, constraints, queries


@given(relations())
def test_relation_to_pb(relation: Relation):
    """Test that Relation objects are correctly packed into the associate protobuf type."""

    actual_relation_value = relation.value
    constraint = relation.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType

    if type(actual_relation_value) == bool:
        expected_relation_value = constraint.relation.val.b
    elif type(actual_relation_value) == int:
        expected_relation_value = constraint.relation.val.i
    elif type(actual_relation_value) == float:
        expected_relation_value = constraint.relation.val.f
    elif type(actual_relation_value) == str:
        expected_relation_value = constraint.relation.val.s
    else:
        assert False

    assert actual_relation_value == expected_relation_value


@given(relations())
def test_relation_from_pb(relation: Relation):
    """Test that Relation objects are correctly unpacked from the associated protobuf type."""

    constraint_pb = relation.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
    relation_pb = constraint_pb.relation

    expected_relation = Relation.from_pb(relation_pb)

    assert relation == expected_relation


@given(ranges())
def test_range_to_pb(range_: Range):
    """Test that Range objects are correctly packed into the associated protobuf type."""

    actual_range_values = range_._values
    range_type = type(range_._values[0])
    constraint = range_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType

    if range_type == str:
        value_pair = constraint.range_.s
    elif range_type == int:
        value_pair = constraint.range_.i
    elif range_type == float:
        value_pair = constraint.range_.f
    else:
        assert False

    expected_range_values = value_pair.first, value_pair.second
    assert actual_range_values == expected_range_values


@given(ranges())
def test_range_from_pb(range_: Range):
    """Test that Range objects are correctly unpacked from the associated protobuf type."""

    constraint_pb = range_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
    expected_range = Range.from_pb(constraint_pb.range_)

    assert range_ == expected_range


@given(query_sets())
def test_set_from_pb(set_: Set):
    """Test that Set objects are correctly unpacked from the associated protobuf type."""

    constraint_pb = set_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
    expected_set = Set.from_pb(constraint_pb.set_)

    assert set_ == expected_set


@given(and_constraints())
def test_and_from_pb(and_: And):
    """Test that And objects are correctly unpacked from the associated protobuf type."""

    constraint_pb = and_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
    expected_and = And.from_pb(constraint_pb.and_)

    assert and_ == expected_and


@given(or_constraints())
def test_or_from_pb(or_: Or):
    """Test that Or objects are correctly unpacked from the associated protobuf type."""

    constraint_pb = or_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
    expected_or = Or.from_pb(constraint_pb.or_)

    assert or_ == expected_or


@given(constraints())
def test_constraint_from_pb(constraint: Constraint):
    """Test that Constraint objects are correctly unpacked from the associated protobuf type."""

    constraint_pb = constraint.to_pb()
    expected_constraint = Constraint.from_pb(constraint_pb)

    assert constraint == expected_constraint


@given(queries())
def test_query_from_pb(query: Query):
    """Test that Query objects are correctly unpacked from the associated protobuf type."""

    query_pb = query.to_pb()
    expected_query = Query.from_pb(query_pb)

    assert query == expected_query
