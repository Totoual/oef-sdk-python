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

from hypothesis import given

from oef import query_pb2
from oef.query import Relation, Range, Set, And, Or, Constraint, Query, Eq, In
from oef.schema import AttributeSchema
from test.hypothesis.strategies import relations, ranges, query_sets, and_constraints, or_constraints, constraints, queries


class TestRelation:

    @given(relations())
    def test_to_pb(self, relation: Relation):
        """Test that Relation objects are correctly packed into the associate protobuf type."""

        actual_relation_value = relation.value
        constraint = relation.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType

        if type(actual_relation_value) == bool:
            expected_relation_value = constraint.relation.val.b
        elif type(actual_relation_value) == int:
            expected_relation_value = constraint.relation.val.i
        elif type(actual_relation_value) == float:
            expected_relation_value = constraint.relation.val.d
        elif type(actual_relation_value) == str:
            expected_relation_value = constraint.relation.val.s
        else:
            assert False

        assert actual_relation_value == expected_relation_value

    @given(relations())
    def test_from_pb(self, relation: Relation):
        """Test that Relation objects are correctly unpacked from the associated protobuf type."""

        constraint_pb = relation.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
        relation_pb = constraint_pb.relation

        expected_relation = Relation.from_pb(relation_pb)

        assert relation == expected_relation

    def test_eq_when_not_equal(self):
        a_relation = Eq("foo")
        not_a_relation = tuple()

        assert a_relation != not_a_relation


class TestRange:

    @given(ranges())
    def test_to_pb(self, range_: Range):
        """Test that Range objects are correctly packed into the associated protobuf type."""

        actual_range_values = range_.values
        range_type = type(range_.values[0])
        constraint = range_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType

        if range_type == str:
            value_pair = constraint.range_.s
        elif range_type == int:
            value_pair = constraint.range_.i
        elif range_type == float:
            value_pair = constraint.range_.d
        else:
            assert False

        expected_range_values = value_pair.first, value_pair.second
        assert actual_range_values == expected_range_values

    @given(ranges())
    def test_from_pb(self, range_: Range):
        """Test that Range objects are correctly unpacked from the associated protobuf type."""

        constraint_pb = range_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
        expected_range = Range.from_pb(constraint_pb.range_)

        assert range_ == expected_range

    def test_eq_when_not_equal(self):
        a_range = Range(("foo", "bar"))
        not_a_range = tuple()

        assert a_range != not_a_range


class TestSet:

    @given(query_sets())
    def test_from_pb(self, set_: Set):
        """Test that Set objects are correctly unpacked from the associated protobuf type."""

        constraint_pb = set_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
        expected_set = Set.from_pb(constraint_pb.set_)

        assert set_ == expected_set

    def test_eq_when_not_equal(self):
        a_set = In(["foo", "bar"])
        not_a_set = tuple()

        assert a_set != not_a_set


class TestAnd:

    @given(and_constraints())
    def test_from_pb(self, and_: And):
        """Test that And objects are correctly unpacked from the associated protobuf type."""

        constraint_pb = and_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
        expected_and = And.from_pb(constraint_pb.and_)

        assert and_ == expected_and

    def test_eq_when_not_equal(self):
        a_and = And([])
        not_a_and = tuple()

        assert a_and != not_a_and


class TestOr:

    @given(or_constraints())
    def test_or_from_pb(self, or_: Or):
        """Test that Or objects are correctly unpacked from the associated protobuf type."""

        constraint_pb = or_.to_pb()  # type: query_pb2.Query.Constraint.ConstraintType
        expected_or = Or.from_pb(constraint_pb.or_)

        assert or_ == expected_or

    def test_eq_when_not_equal(self):
        a_or = Or([])
        not_a_or = tuple()

        assert a_or != not_a_or


class TestConstraint:

    @given(constraints())
    def test_from_pb(self, constraint: Constraint):
        """Test that Constraint objects are correctly unpacked from the associated protobuf type."""

        constraint_pb = constraint.to_pb()
        expected_constraint = Constraint.from_pb(constraint_pb)

        assert constraint == expected_constraint

    def test_eq_when_not_equal(self):
        a_constraint = Constraint(AttributeSchema("foo", str, True), And([]))
        not_a_constraint = tuple()

        assert a_constraint != not_a_constraint


class TestQuery:

    @given(queries())
    def test_from_pb(self, query: Query):
        """Test that Query objects are correctly unpacked from the associated protobuf type."""

        query_pb = query.to_pb()
        expected_query = Query.from_pb(query_pb)

        assert query == expected_query

    def test_eq_when_not_equal(self):
        a_query = Query([])
        not_a_query = tuple()

        assert a_query != not_a_query
