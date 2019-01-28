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
from oef.query import Relation, Range, Set, And, Or, Constraint, Query, Eq, In, Not
from test.hypothesis.strategies import relations, ranges, query_sets, and_constraints, or_constraints, constraints, \
    queries, not_constraints


class TestRelation:

    @given(relations())
    def test_serialization(self, relation: Relation):
        """Test that serialization and deserialization of ``Relation`` objects work correctly."""

        actual_relation = relation
        relation_pb = actual_relation.to_pb()  # type: query_pb2.Query.Relation
        expected_relation = Relation.from_pb(relation_pb)

        assert actual_relation == expected_relation

    def test_eq_when_not_equal(self):
        a_relation = Eq("foo")
        not_a_relation = tuple()

        assert a_relation != not_a_relation


class TestRange:

    @given(ranges())
    def test_serialization(self, range_: Range):
        """Test that serialization and deserialization of ``Range`` objects work correctly."""

        actual_range = range_
        range_pb = actual_range.to_pb()  # type: query_pb2.Query.Relation
        expected_range = Range.from_pb(range_pb)

        assert actual_range == expected_range

    def test_eq_when_not_equal(self):
        a_range = Range(("foo", "bar"))
        not_a_range = tuple()

        assert a_range != not_a_range


class TestSet:

    @given(query_sets())
    def test_serialization(self, set_: Set):
        """Test that serialization and deserialization of ``Set`` objects work correctly."""
        actual_set = set_
        set_pb = actual_set.to_pb()
        expected_set = Set.from_pb(set_pb)

        assert actual_set == expected_set

    def test_eq_when_not_equal(self):
        a_set = In(["foo", "bar"])
        not_a_set = tuple()

        assert a_set != not_a_set


class TestConstraint:

    @given(constraints())
    def test_serialization(self, constraint: Constraint):
        """Test that serialization and deserialization of ``Constraint`` objects work correctly."""
        actual_constraint = constraint
        constraint_pb = constraint.to_pb()
        expected_constraint = Constraint.from_pb(constraint_pb)

        assert actual_constraint == expected_constraint

    def test_eq_when_not_equal(self):
        a_constraint = Constraint("foo", In([]))
        not_a_constraint = tuple()

        assert a_constraint != not_a_constraint


class TestAnd:

    @given(and_constraints())
    def test_serialization(self, and_: And):
        """Test that serialization and deserialization of ``And`` objects work correctly."""

        actual_and = and_
        and_pb = and_.to_pb()  # type: query_pb2.Query.ConstraintExpr.And
        expected_and = And.from_pb(and_pb)

        assert actual_and == expected_and

    def test_eq_when_not_equal(self):
        a_and = And([])
        not_a_and = tuple()

        assert a_and != not_a_and


class TestOr:

    @given(or_constraints())
    def test_serialization(self, or_: Or):
        """Test that serialization and deserialization of ``Or`` objects work correctly."""

        actual_or = or_
        or_pb = or_.to_pb()  # type: query_pb2.Query.ConstraintExpr.Or
        expected_or = Or.from_pb(or_pb)

        assert actual_or == expected_or

    def test_eq_when_not_equal(self):
        a_or = Or([])
        not_a_or = tuple()

        assert a_or != not_a_or


class TestNot:

    @given(not_constraints())
    def test_serialization(self, not_: Not):
        """Test that serialization and deserialization of ``Not`` objects work correctly."""

        actual_not = not_
        not_pb = not_.to_pb()  # type: query_pb2.Query.ConstraintExpr.Not
        expected_not = Not.from_pb(not_pb)

        assert actual_not == expected_not

    def test_eq_when_not_equal(self):
        a_or = Or([])
        not_a_or = tuple()

        assert a_or != not_a_or


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
