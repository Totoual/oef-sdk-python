# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
from abc import ABC
from enum import Enum
from typing import Union, Tuple, List, Optional

import oef.query_pb2 as query_pb2

from oef.schema import ATTRIBUTE_TYPES, AttributeSchema, DataModel, ProtobufSerializable

RANGE_TYPES = Union[Tuple[str, str], Tuple[int, int], Tuple[float, float]]


class ConstraintType(ProtobufSerializable, ABC):

    @classmethod
    def from_pb(cls, constraint_pb: query_pb2.Query.Constraint.ConstraintType):
        constraint_case = constraint_pb.WhichOneof("constraint")
        if constraint_case == "relation":
            return Relation.from_pb(constraint_pb.relation)
        elif constraint_case == "set_":
            return Set.from_pb(constraint_pb.set_)
        elif constraint_case == "range_":
            return Range.from_pb(constraint_pb.range_)
        elif constraint_case == "and_":
            return And.from_pb(constraint_pb.and_)
        elif constraint_case == "or_":
            return Or.from_pb(constraint_pb.or_)
        else:
            raise Exception("No valid constraint type.")


class Relation(ConstraintType):

    def __init__(self, value: ATTRIBUTE_TYPES) -> None:
        self.value = value

    @property
    def operator(self) -> query_pb2.Query.Relation:
        raise NotImplementedError

    @classmethod
    def from_pb(cls, relation: query_pb2.Query.Relation):
        relations_from_pb = {
            query_pb2.Query.Relation.GTEQ: GtEq,
            query_pb2.Query.Relation.GT: Gt,
            query_pb2.Query.Relation.LTEQ: LtEq,
            query_pb2.Query.Relation.LT: Lt,
            query_pb2.Query.Relation.NOTEQ: NotEq,
            query_pb2.Query.Relation.EQ: Eq
        }

        value_case = relation.val.WhichOneof("value")
        if value_case == "s":
            return relations_from_pb[relation.op](relation.val.s)
        elif value_case == "b":
            return relations_from_pb[relation.op](relation.val.b)
        elif value_case == "i":
            return relations_from_pb[relation.op](relation.val.i)
        elif value_case == "f":
            return relations_from_pb[relation.op](relation.val.f)

    def to_pb(self):
        relation = query_pb2.Query.Relation()
        relation.op = self.operator()
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
        constraint_type = query_pb2.Query.Constraint.ConstraintType()
        constraint_type.relation.CopyFrom(relation)
        return constraint_type


class Eq(Relation):

    def operator(self):
        return query_pb2.Query.Relation.EQ


class NotEq(Relation):

    def operator(self):
        return query_pb2.Query.Relation.NOTEQ


class Lt(Relation):

    def operator(self):
        return query_pb2.Query.Relation.LT


class LtEq(Relation):

    def operator(self):
        return query_pb2.Query.Relation.LTEQ


class Gt(Relation):

    def operator(self):
        return query_pb2.Query.Relation.GT


class GtEq(Relation):

    def operator(self):
        return query_pb2.Query.Relation.GTEQ


class Range(ConstraintType):
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
        constraint_type = query_pb2.Query.Constraint.ConstraintType()
        constraint_type.range_.CopyFrom(range_)
        return constraint_type

    @classmethod
    def from_pb(cls, range_pb: query_pb2.Query.Range):
        range_case = range_pb.WhichOneof("pair")
        if range_case == "s":
            values = (range_pb.s.first, range_pb.s.second)
        elif range_case == "i":
            values = (range_pb.i.first, range_pb.i.second)
        elif range_case == "f":
            values = (range_pb.f.first, range_pb.f.second)
        else:
            raise Exception("")
        return cls(values)


SET_TYPES = Union[List[float], List[str], List[bool], List[int]]


class Set(ConstraintType):

    class Operator(Enum):
        IN = 0
        NOT_IN = 1

    def __init__(self, values: SET_TYPES, operator: Operator) -> None:
        self._values = values
        self._operator = operator

    @property
    def operator(self) -> query_pb2.Query.Set:
        raise NotImplementedError

    def to_pb(self):
        set_ = query_pb2.Query.Set()
        set_.op = self.operator()
        if isinstance(self._values[0], str):
            values = query_pb2.Query.Set.Values.Strings()
            values.vals.extend(self._values)
            set_.vals.s.CopyFrom(values)
        elif isinstance(self._values[0], bool):  # warning: order matters, bools before ints.
            values = query_pb2.Query.Set.Values.Bools()
            values.vals.extend(self._values)
            set_.vals.b.CopyFrom(values)
        elif isinstance(self._values[0], int):
            values = query_pb2.Query.Set.Values.Ints()
            values.vals.extend(self._values)
            set_.vals.i.CopyFrom(values)
        elif isinstance(self._values[0], float):
            values = query_pb2.Query.Set.Values.Floats()
            values.vals.extend(self._values)
            set_.vals.f.CopyFrom(values)
        constraint_type = query_pb2.Query.Constraint.ConstraintType()
        constraint_type.set_.CopyFrom(set_)
        return constraint_type

    @classmethod
    def from_pb(cls, set_pb: query_pb2.Query.Set):
        op_from_pb = {
            query_pb2.Query.Set.IN: In,
            query_pb2.Query.Set.NOTIN: NotIn
        }
        value_case = set_pb.vals.WhichOneof("values")
        if value_case == "s":
            return op_from_pb[set_pb.op](set_pb.vals.s.vals)
        elif value_case == "b":
            return op_from_pb[set_pb.op](set_pb.vals.b.vals)
        elif value_case == "i":
            return op_from_pb[set_pb.op](set_pb.vals.i.vals)
        elif value_case == "f":
            return op_from_pb[set_pb.op](set_pb.vals.f.vals)


class In(Set):

    def __init__(self, values: SET_TYPES):
        super().__init__(values, Set.Operator.IN)

    def operator(self):
        return query_pb2.Query.Set.IN


class NotIn(Set):

    def __init__(self, values: SET_TYPES):
        super().__init__(values, Set.Operator.NOT_IN)

    def operator(self):
        return query_pb2.Query.Set.NOTIN


CONSTRAINT_TYPES = Union[Relation, Range, Set]


class And(ConstraintType):
    def __init__(self, constraints: List[CONSTRAINT_TYPES]) -> None:
        self._constraints = constraints

    def to_pb(self):
        and_pb = query_pb2.Query.Constraint.ConstraintType.And()
        and_pb.expr.extend([constraint.to_pb() for constraint in self._constraints])
        constraint_type = query_pb2.Query.Constraint.ConstraintType()
        constraint_type.and_.CopyFrom(and_pb)
        return constraint_type

    @classmethod
    def from_pb(cls, constraint_pb: query_pb2.Query.Constraint.ConstraintType.And):
        expr = [ConstraintType.from_pb(c) for c in constraint_pb.expr]
        return cls(expr)


class Or(ConstraintType):
    def __init__(self, constraints: List[CONSTRAINT_TYPES]) -> None:
        self._constraints = constraints

    def to_pb(self):
        or_pb = query_pb2.Query.Constraint.ConstraintType.Or()
        or_pb.expr.extend([constraint.to_pb() for constraint in self._constraints])
        constraint_type = query_pb2.Query.Constraint.ConstraintType()
        constraint_type.or_.CopyFrom(or_pb)
        return constraint_type

    @classmethod
    def from_pb(cls, constraint_pb: query_pb2.Query.Constraint.ConstraintType.Or):
        expr = [ConstraintType.from_pb(c) for c in constraint_pb.expr]
        return cls(expr)


CONSTRAINT_TYPES = Union[Relation, Range, Set, And, Or]


class Constraint(object):
    def __init__(self,
                 attribute: AttributeSchema,
                 constraint: CONSTRAINT_TYPES) -> None:
        self._attribute = attribute
        self._constraint = constraint

    def to_pb(self):
        constraint = query_pb2.Query.Constraint()
        constraint.attribute.CopyFrom(self._attribute.to_pb())
        constraint.constraint.CopyFrom(self._constraint.to_pb())
        return constraint

    @classmethod
    def from_pb(cls, constraint_pb: query_pb2.Query.Constraint):
        constraint_type = ConstraintType.from_pb(constraint_pb.constraint)
        return cls(AttributeSchema.from_pb(constraint_pb.attribute), constraint_type)


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

    def to_pb(self):
        query = query_pb2.Query.Model()
        query.constraints.extend([constraint.to_pb() for constraint in self._constraints])
        if self._model is not None:
            query.model.CopyFrom(self._model.to_pb())
        return query

    @classmethod
    def from_pb(cls, query: query_pb2.Query.Model):
        constraints = [Constraint.from_pb(constraint_pb) for constraint_pb in query.constraints]
        return cls(constraints, DataModel.from_pb(query.model) if query.HasField("model") else None)

    def __eq__(self, other):
        if type(other) != Query:
            return False
        return self._constraints == other._constraints and self._model == other._model
