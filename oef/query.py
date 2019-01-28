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

from abc import ABC, abstractmethod
from typing import Union, Tuple, List, Optional

import oef.query_pb2 as query_pb2
from oef.schema import ATTRIBUTE_TYPES, AttributeSchema, DataModel, ProtobufSerializable, Description, Location

RANGE_TYPES = Union[Tuple[str, str], Tuple[int, int], Tuple[float, float], Tuple[Location, Location]]


class ConstraintExpr(ProtobufSerializable, ABC):
    """
    This class is used to represent a constraint expression.
    """

    @abstractmethod
    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if an attribute value satisfies the constraint.
        The implementation depends on the constraint type.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """

    @staticmethod
    def _to_pb(expression):
        constraint_expr_pb = query_pb2.Query.ConstraintExpr()
        expression_pb = expression.to_pb()
        if isinstance(expression, And):
            constraint_expr_pb.and_.CopyFrom(expression_pb)
        elif isinstance(expression, Or):
            constraint_expr_pb.or_.CopyFrom(expression_pb)
        elif isinstance(expression, Not):
            constraint_expr_pb.not_.CopyFrom(expression_pb)
        elif isinstance(expression, Constraint):
            constraint_expr_pb.constraint.CopyFrom(expression_pb)

        return constraint_expr_pb

    @staticmethod
    def _from_pb(expression_pb):
        expression = expression_pb.WhichOneof("expression")
        if expression == "and_":
            return And.from_pb(expression_pb.and_)
        elif expression == "or_":
            return Or.from_pb(expression_pb.or_)
        elif expression == "not_":
            return Not.from_pb(expression_pb.not_)
        elif expression == "constraint":
            return Constraint.from_pb(expression_pb.constraint)


class And(ConstraintExpr):
    """
    A constraint type that allows you to specify a conjunction of constraints.
    That is, the ``And`` constraint is satisfied whenever all the constraints that constitute the and are satisfied.

    Examples:

        # >>> # all the books whose title is between 'I' and 'J' (alphanumeric order) but not equal to 'It'
        # >>> c = Constraint(AttributeSchema("title", str, True),   And([Range(("I", "J")), NotEq("It")]))
        # >>> c.check(Description({"title": "I, Robot"}))
        # True
        # >>> c.check(Description({"title": "It"}))
        # False
        # >>> c.check(Description({"title": "1984"}))
        # False
    """

    def __init__(self, constraints: List[ConstraintExpr]) -> None:
        """
        Initialize an ``And`` constraint.

        :param constraints: the list of constraints to be interpreted in conjunction.
        """
        self.constraints = constraints

    def to_pb(self):
        """
        From an instance of ``And`` to its associated Protobuf object.

        :return: the ConstraintExpr Protobuf object that contains the ``And`` constraint.
        """
        and_pb = query_pb2.Query.ConstraintExpr.And()
        constraint_expr_pbs = [ConstraintExpr._to_pb(constraint) for constraint in self.constraints]
        and_pb.expr.extend(constraint_expr_pbs)
        return and_pb

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value satisfies all the constraints of the ``And`` constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return all(expr.check(value) for expr in self.constraints)

    @classmethod
    def from_pb(cls, constraint_pb: query_pb2.Query.ConstraintExpr.And):
        """
        From the And Protobuf object to the associated instance of ``And``.

        :param constraint_pb: the Protobuf object that represents the ``And`` constraint.
        :return: an instance of ``And`` equivalent to the Protobuf object.
        """

        expr = [ConstraintExpr._from_pb(c) for c in constraint_pb.expr]
        return cls(expr)

    def __eq__(self, other):
        if type(other) != And:
            return False
        else:
            return self.constraints == other.constraints


class Or(ConstraintExpr):
    """
    A constraint type that allows you to specify a disjunction of constraints.
    That is, the Or constraint is satisfied whenever at least one of the constraints
    that constitute the or is satisfied.

    Examples:

        >>> # all the books that have been published either before the year 1960 or after the year 1970
        >>> c = Constraint(AttributeSchema("year", int, True),   Or([Lt(1960), Gt(1970)]))
        >>> c.check(Description({"year": 1950}))
        True
        >>> c.check(Description({"year": 1975}))
        True
        >>> c.check(Description({"year": 1960}))
        False
        >>> c.check(Description({"year": 1970}))
        False
    """

    def __init__(self, constraints: List[ConstraintExpr]) -> None:
        """
        Initialize an ``Or`` constraint.

        :param constraints: the list of constraints to be interpreted in disjunction.
        """
        self.constraints = constraints

    def to_pb(self):
        """
        From an instance of ``Or`` to its associated Protobuf object.

        :return: the ConstraintType Protobuf object that contains the ``Or`` constraint.
        """

        or_pb = query_pb2.Query.ConstraintExpr.Or()
        constraint_expr_pbs = [ConstraintExpr._to_pb(constraint) for constraint in self.constraints]
        or_pb.expr.extend(constraint_expr_pbs)
        return or_pb

    @classmethod
    def from_pb(cls, constraint_pb: query_pb2.Query.ConstraintExpr.Or):
        """
        From the ``Or`` Protobuf object to the associated instance of Or.

        :param constraint_pb: the Protobuf object that represents the ``Or`` constraint.
        :return: an instance of ``Or`` equivalent to the Protobuf object.
        """
        expr = [ConstraintExpr._from_pb(c) for c in constraint_pb.expr]
        return cls(expr)

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value satisfies one of the constraints of the ``Or`` constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return any(expr.check(value) for expr in self.constraints)

    def __eq__(self, other):
        if type(other) != Or:
            return False
        else:
            return self.constraints == other.constraints


class Not(ConstraintExpr):
    """
    A constraint type that allows you to specify a negation of a constraint.
    That is, the Not constraint is satisfied whenever the constraint
    that constitutes the Not expression is not satisfied.

    Examples:
        # todo examples for Not constraint expression
        >>> True
    """

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        pass

    def __init__(self, constraint: ConstraintExpr) -> None:
        self.constraint = constraint

    def to_pb(self):
        not_pb = query_pb2.Query.ConstraintExpr.Not()
        constraint_expr_pb = ConstraintExpr._to_pb(self.constraint)
        not_pb.expr.CopyFrom(constraint_expr_pb)
        return not_pb

    @classmethod
    def from_pb(cls, constraint_pb: query_pb2.Query.ConstraintExpr.Not):
        expression = ConstraintExpr._from_pb(constraint_pb.expr)
        return cls(expression)

    def __eq__(self, other):
        if type(other) != Not:
            return False
        else:
            return self.constraint == other.constraint


class ConstraintType(ProtobufSerializable, ABC):
    """
    This class is used to represent a constraint type.
    """

    @abstractmethod
    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if an attribute value satisfies the constraint.
        The implementation depends on the constraint type.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """


class Relation(ConstraintType, ABC):
    """
    A constraint type that allows you to impose specific values
    for the attributes.

    The specific operator of the relation is defined in the
    subclasses that extend this class.
    """

    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        """
        Initialize a Relation object.

        :param value: the right value of the relation.
        """
        self.value = value

    @property
    @abstractmethod
    def operator(self) -> query_pb2.Query.Relation:
        """The operator of the relation."""

    @classmethod
    def from_pb(cls, relation: query_pb2.Query.Relation):
        """
        From the Relation Protobuf object to the associated
        instance of a subclass of Relation.

        :param relation: the Protobuf object that represents the relation constraint.
        :return: an instance of one of the subclasses of Relation.
        """

        relations_from_pb = {
            query_pb2.Query.Relation.GTEQ: GtEq,
            query_pb2.Query.Relation.GT: Gt,
            query_pb2.Query.Relation.LTEQ: LtEq,
            query_pb2.Query.Relation.LT: Lt,
            query_pb2.Query.Relation.NOTEQ: NotEq,
            query_pb2.Query.Relation.EQ: Eq
        }

        relation_class = relations_from_pb[relation.op]
        value_case = relation.val.WhichOneof("value")
        if value_case == "s":
            return relation_class(relation.val.s)
        elif value_case == "b":
            return relation_class(relation.val.b)
        elif value_case == "i":
            return relation_class(relation.val.i)
        elif value_case == "d":
            return relation_class(relation.val.d)
        elif value_case == "l":
            return relation_class(Location.from_pb(relation.val.l))

    def to_pb(self) -> query_pb2.Query.Relation:
        """
        From an instance of Relation to its associated Protobuf object.

        :return: the ConstraintType Protobuf object that contains the relation.
        """
        relation = query_pb2.Query.Relation()
        relation.op = self.operator()
        query_value = query_pb2.Query.Value()
        if isinstance(self.value, bool):
            query_value.b = self.value
        elif isinstance(self.value, int):
            query_value.i = self.value
        elif isinstance(self.value, float):
            query_value.d = self.value
        elif isinstance(self.value, str):
            query_value.s = self.value
        elif isinstance(self.value, Location):
            query_value.l.CopyFrom(self.value.to_pb())
        relation.val.CopyFrom(query_value)
        return relation

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        else:
            return self.value == other.value


class Eq(Relation):
    """
    The equality relation.

    Examples:
        >>> # all the books whose author is Stephen King
        >>> c = Constraint(AttributeSchema("author", str, True),  Eq("Stephen King"))
        >>> c.check(Description({"author": "Stephen King"}))
        True
        >>> c.check(Description({"author": "George Orwell"}))
        False

    """

    def operator(self):
        return query_pb2.Query.Relation.EQ

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value is equal to the value of the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return value == self.value


class NotEq(Relation):
    """
    The non-equality relation.

    Examples:
        >>> # all the books that are not of the genre Horror
        >>> c = Constraint(AttributeSchema("genre", str, True),   NotEq("horror"))
        >>> c.check(Description({"genre": "non-fiction"}))
        True
        >>> c.check(Description({"author": "horror"}))
        False

    """

    def operator(self):
        return query_pb2.Query.Relation.NOTEQ

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value is not equal to the value of the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return value != self.value


class Lt(Relation):
    """Less-than relation.

    Examples:
        >>> # all the books published before 1990
        >>> c = Constraint(AttributeSchema("year", int, True), Lt(1990))
        >>> c.check(Description({"year": 1985}))
        True
        >>> c.check(Description({"year": 2000}))
        False

    """

    def operator(self):
        return query_pb2.Query.Relation.LT

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value is less than the value of the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return value < self.value


class LtEq(Relation):
    """
    Less-than-equal relation.

    Examples:
        >>> # all the books published before 1990, 1990 included
        >>> c = Constraint(AttributeSchema("year", int, True), LtEq(1990))
        >>> c.check(Description({"year": 1990}))
        True
        >>> c.check(Description({"year": 1991}))
        False

    """

    def operator(self):
        return query_pb2.Query.Relation.LTEQ

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value is less than or equal to the value of the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return value <= self.value


class Gt(Relation):
    """
    Greater-than relation.

    Examples:
        >>> # all the books with rating greater than 4.0
        >>> c = Constraint(AttributeSchema("average_rating", float, True), Gt(4.0))
        >>> c.check(Description({"average_rating": 4.5}))
        True
        >>> c.check(Description({"average_rating": 3.0}))
        False
    """

    def operator(self):
        return query_pb2.Query.Relation.GT

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value is greater than the value of the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return value > self.value


class GtEq(Relation):
    """
    Greater-than-equal relation.

    Examples:
        >>> # all the books published after 2000, included
        >>> c = Constraint(AttributeSchema("year", int, True), GtEq(2000))
        >>> c.check(Description({"year": 2000}))
        True
        >>> c.check(Description({"year": 1990}))
        False
    """

    def operator(self):
        return query_pb2.Query.Relation.GTEQ

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value greater than or equal to the value of the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return value >= self.value


class Range(ConstraintType):
    """
    A constraint type that allows you to restrict the values of the attribute in a given range.

    Examples:
        >>> # all the books published after 2000, included
        >>> c = Constraint(AttributeSchema("year", int, True), Range((2000, 2005)))
        >>> c.check(Description({"year": 2000}))
        True
        >>> c.check(Description({"year": 2005}))
        True
        >>> c.check(Description({"year": 1990}))
        False
        >>> c.check(Description({"year": 2010}))
        False
    """

    def __init__(self, values: RANGE_TYPES) -> None:
        """
        Initialize a range constraint type.

        :param values: a pair of ``int``, a pair of ``str``, or a pair of ``float`.
        """
        self.values = values

    def to_pb(self) -> query_pb2.Query:
        """
        From an instance of Range to its associated Protobuf object.

        :return: the ConstraintType Protobuf object that contains the range.
        """
        range_ = query_pb2.Query.Range()
        if type(self.values[0]) == str:
            values = query_pb2.Query.StringPair()
            values.first = self.values[0]
            values.second = self.values[1]
            range_.s.CopyFrom(values)
        elif type(self.values[0]) == int:
            values = query_pb2.Query.IntPair()
            values.first = self.values[0]
            values.second = self.values[1]
            range_.i.CopyFrom(values)
        elif type(self.values[0]) == float:
            values = query_pb2.Query.DoublePair()
            values.first = self.values[0]
            values.second = self.values[1]
            range_.d.CopyFrom(values)
        elif type(self.values[0]) == Location:
            values = query_pb2.Query.LocationPair()
            values.first.CopyFrom(self.values[0].to_pb())
            values.second.CopyFrom(self.values[1].to_pb())
            range_.l.CopyFrom(values)
        return range_

    @classmethod
    def from_pb(cls, range_pb: query_pb2.Query.Range):
        """
        From the Range Protobuf object to the associated instance of ``Range``.

        :param range_pb: the Protobuf object that represents the range.
        :return: an instance of ``Range`` equivalent to the Protobuf object provided as input.
        """

        range_case = range_pb.WhichOneof("pair")
        if range_case == "s":
            return cls((range_pb.s.first, range_pb.s.second))
        elif range_case == "i":
            return cls((range_pb.i.first, range_pb.i.second))
        elif range_case == "d":
            return cls((range_pb.d.first, range_pb.d.second))
        elif range_case == "l":
            return cls((Location.from_pb(range_pb.l.first), Location.from_pb(range_pb.l.second)))

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value is in the range specified by the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        left, right = self.values
        return left <= value <= right

    def __eq__(self, other):
        if type(other) != Range:
            return False
        else:
            return self.values == other.values


SET_TYPES = Union[List[float], List[str], List[bool], List[int], List[Location]]


class Set(ConstraintType, ABC):
    """
    A constraint type that allows you to restrict the values of the attribute in a specific set.

    The specific operator of the relation is defined in the subclasses that extend this class.
    """

    def __init__(self, values: SET_TYPES) -> None:
        """
        Initialize a Set constraint.

        :param values: a list of values for the set relation.
        """
        self.values = values

    @property
    @abstractmethod
    def operator(self) -> query_pb2.Query.Set:
        """The operator over the set."""

    def to_pb(self):
        """
        From an instance of one of the subclasses of Set to its associated Protobuf object.

        :return: the ConstraintType Protobuf object that contains the set constraint.
        """
        set_ = query_pb2.Query.Set()
        set_.op = self.operator()

        value_type = type(self.values[0]) if len(self.values) > 0 else str

        if value_type == str:
            values = query_pb2.Query.Set.Values.Strings()
            values.vals.extend(self.values)
            set_.vals.s.CopyFrom(values)
        elif value_type == bool:
            values = query_pb2.Query.Set.Values.Bools()
            values.vals.extend(self.values)
            set_.vals.b.CopyFrom(values)
        elif value_type == int:
            values = query_pb2.Query.Set.Values.Ints()
            values.vals.extend(self.values)
            set_.vals.i.CopyFrom(values)
        elif value_type == float:
            values = query_pb2.Query.Set.Values.Doubles()
            values.vals.extend(self.values)
            set_.vals.d.CopyFrom(values)
        elif value_type == Location:
            values = query_pb2.Query.Set.Values.Locations()
            values.vals.extend([value.to_pb() for value in self.values])
            set_.vals.l.CopyFrom(values)

        return set_

    @classmethod
    def from_pb(cls, set_pb: query_pb2.Query.Set):
        """
        From the Set Protobuf object to the associated
        instance of a subclass of Set.

        :param set_pb: the Protobuf object that represents the set constraint.
        :return: the object of one of the subclasses of ``Set``.
        """
        op_from_pb = {
            query_pb2.Query.Set.IN: In,
            query_pb2.Query.Set.NOTIN: NotIn
        }
        set_class = op_from_pb[set_pb.op]
        value_case = set_pb.vals.WhichOneof("values")
        if value_case == "s":
            return set_class(set_pb.vals.s.vals)
        elif value_case == "b":
            return set_class(set_pb.vals.b.vals)
        elif value_case == "i":
            return set_class(set_pb.vals.i.vals)
        elif value_case == "d":
            return set_class(set_pb.vals.d.vals)
        elif value_case == "l":
            locations = [Location.from_pb(loc) for loc in set_pb.vals.l.vals]
            return set_class(locations)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.values == other.values


class In(Set):
    """
    Class that implements the 'in set' constraint type.
    That is, the value of attribute over which the constraint is defined
    must be in the set of values provided.

    Examples:

        >>> # all the books whose genre is one of `Horror`, `Science fiction`, `Non-fiction`
        >>> c = Constraint(AttributeSchema("genre", str, True), In(["horror", "science fiction", "non-fiction"]))
        >>> c.check(Description({"genre": "horror"}))
        True
        >>> c.check(Description({"genre": "thriller"}))
        False

    """

    def __init__(self, values: SET_TYPES):
        super().__init__(values)

    def operator(self):
        return query_pb2.Query.Set.IN

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value is in the set of values specified by the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return value in self.values


class NotIn(Set):
    """
    Class that implements the 'not in set' constraint type.
    That is, the value of attribute over which the constraint is defined
    must be not in the set of values provided.

    Examples:

        >>> # all the books that have not been published neither in 1990, nor in 1995, nor in 2000
        >>> c = Constraint(AttributeSchema("year", int, True), NotIn([1990, 1995, 2000]))
        >>> c.check(Description({"year": 1991}))
        True
        >>> c.check(Description({"year": 2000}))
        False

    """

    def __init__(self, values: SET_TYPES):
        super().__init__(values)

    def operator(self):
        return query_pb2.Query.Set.NOTIN

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        """
        Check if a value is not in the set of values specified by the constraint.

        :param value: the value to check.
        :return: ``True`` if the value satisfy the constraint, ``False`` otherwise.
        """
        return value not in self.values


class Distance(ConstraintType):
    """
    Class that implements the 'not in set' constraint type.
    That is, the value of attribute over which the constraint is defined
    must be not in the set of values provided.

    Examples:
    """

    def __init__(self, center: Location, distance: float) -> None:
        self.center = center
        self.distance = distance

    def check(self, value: ATTRIBUTE_TYPES) -> bool:
        raise NotImplementedError

    def to_pb(self):
        pass

    @classmethod
    def from_pb(cls, distance_pb: query_pb2.Query.Distance):
        pass


class Constraint(ProtobufSerializable):
    """
    A class that represent a constraint over an attribute.
    """

    def __init__(self,
                 attribute_name: str,
                 constraint: ConstraintType) -> None:
        self.attribute_name = attribute_name
        self.constraint = constraint

    def to_pb(self):
        """
        Return the associated Protobuf object.

        :return: a Protobuf object equivalent to the caller object.
        """
        constraint = query_pb2.Query.ConstraintExpr.Constraint()
        constraint.attribute_name = self.attribute_name
        constraint_type_pb = self.constraint.to_pb()

        if isinstance(self.constraint, Relation):
            constraint.relation.CopyFrom(constraint_type_pb)
        elif isinstance(self.constraint, Range):
            constraint.range_.CopyFrom(constraint_type_pb)
        elif isinstance(self.constraint, Set):
            constraint.set_.CopyFrom(constraint_type_pb)
        elif isinstance(self.constraint, Distance):
            constraint.distance.CopyFrom(constraint_type_pb)
        else:
            assert False

        return constraint

    @classmethod
    def from_pb(cls, constraint_pb: query_pb2.Query.ConstraintExpr.Constraint):
        """
        From the ``Constraint`` Protobuf object to the associated instance of ``Constraint``.

        :param constraint_pb: the Protobuf object that represents the ``Constraint`` object.
        :return: an instance of ``Constraint`` equivalent to the Protobuf object provided in input.
        """

        constraint_case = constraint_pb.WhichOneof("constraint")
        constraint_type = None
        if constraint_case == "relation":
            constraint_type = Relation.from_pb(constraint_pb.relation)
        elif constraint_case == "set_":
            constraint_type = Set.from_pb(constraint_pb.set_)
        elif constraint_case == "range_":
            constraint_type = Range.from_pb(constraint_pb.range_)
        elif constraint_case == "distance":
            constraint_type = Distance.from_pb(constraint_pb.distance)

        return cls(constraint_pb.attribute_name, constraint_type)

    def check(self, description: Description) -> bool:
        """
        Check if a description satisfies the constraint. The implementation depends on the type of the constraint.

        :param description: the description to check.
        :return: ``True`` if the description satisfies the constraint, ``False`` otherwise.

        Examples:
            >>> attr_author = AttributeSchema("author" , str, True, "The author of the book.")
            >>> attr_year   = AttributeSchema("year",    int, True, "The year of publication of the book.")
            >>> c1 = Constraint(attr_author, Eq("Stephen King"))
            >>> c2 = Constraint(attr_year, Gt(1990))
            >>> book_1 = Description({"author": "Stephen King",  "year": 1991})
            >>> book_2 = Description({"author": "George Orwell", "year": 1948})

            The ``"author"`` attribute instantiation satisfies the constraint, so the result is ``True``.
            >>> c1.check(book_1)
            True

            Here, the ``"author"`` does not satisfy the constraints. Hence, the result is ``False``.
            >>> c1.check(book_2)
            False

            In this case, there is a missing field specified by the query, that is ``"year"``
            So the result is ``False``, even in the case it is not required by the schema:
            >>> c2.check(Description({"author": "Stephen King"}))
            False

            If the type of some attribute of the description is not correct, the result is ``False``.
            In this case, the field ``"year"`` has a string instead of an integer:
            >>> c2.check(Description({"author": "Stephen King", "year": "1991"}))
            False

        """
        # if the name of the attribute is not present, return false.
        name = self.attribute.name
        if name not in description.values:
            return False

        # if the type of the value is different from the type of the attribute schema, return false.
        value = description.values[name]
        if type(value) != self.attribute.type:
            return False

        # dispatch the check to the right implementation for the concrete constraint type.
        return self.constraint.check(value)

    def __eq__(self, other):
        if type(other) != Constraint:
            return False
        else:
            return self.attribute_name == other.attribute_name and self.constraint == other.constraint


class Query(ProtobufSerializable):
    """
    Representation of a search that is to be performed. Currently a search is represented as a
    set of key value pairs that must be contained in the description of the service/ agent.

    Examples:

        Return all the books written by Stephen King published after 1990, and available as an e-book:
        >>> attr_author   = AttributeSchema("author" ,         str,   True,  "The author of the book.")
        >>> attr_year     = AttributeSchema("year",            int,   True,  "The year of publication of the book.")
        >>> attr_ebook    = AttributeSchema("ebook_available", bool,  False, "If the book can be sold as an e-book.")
        >>> q = Query([
        ...     Constraint(attr_author, Eq("Stephen King")),
        ...     Constraint(attr_year, Gt(1990)),
        ...     Constraint(attr_ebook, Eq(True))
        ... ])

        With a query, you can check that a `~oef.schema.Description` object satisfies the constraints.
        >>> q.check(Description({"author": "Stephen King", "year": 1991, "ebook_available": True}))
        True
        >>> q.check(Description({"author": "George Orwell", "year": 1948, "ebook_available": False}))
        False

    """

    def __init__(self,
                 constraints: List[Constraint],
                 model: Optional[DataModel] = None) -> None:
        """
        Initialize a query.

        :param constraints: a list of ``Constraint``.
        :param model: the data model where the query is defined.
        """
        self.constraints = constraints
        self.model = model

    def to_pb(self) -> query_pb2.Query.Model:
        """
        Return the associated Protobuf object.

        :return: a Protobuf object equivalent to the caller object.
        """
        query = query_pb2.Query.Model()
        constraint_expr_pbs = [ConstraintExpr._to_pb(constraint) for constraint in self.constraints]
        query.constraints.extend(constraint_expr_pbs)

        if self.model is not None:
            query.model.CopyFrom(self.model.to_pb())
        return query

    @classmethod
    def from_pb(cls, query: query_pb2.Query.Model):
        """
        From the ``Query`` Protobuf object to the associated instance of ``Query``.

        :param query: the Protobuf object that represents the ``Query`` object.
        :return: an instance of ``Query`` equivalent to the Protobuf object provided in input.
        """
        constraints = [ConstraintExpr._from_pb(c) for c in query.constraints]
        return cls(constraints, DataModel.from_pb(query.model) if query.HasField("model") else None)

    def check(self, description: Description) -> bool:
        """
        Check if a description satisfies the constraints of the query.
        The constraints are interpreted as conjunction.

        :param description: the description to check.
        :return: ``True`` if the description satisfies all the constraints, ``False`` otherwise.
        """
        return all(c.check(description) for c in self.constraints)

    def __eq__(self, other):
        if type(other) != Query:
            return False
        return self.constraints == other.constraints and self.model == other.model
