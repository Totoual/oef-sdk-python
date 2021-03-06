# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fipa.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import oef.query_pb2 as query__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='fipa.proto',
  package='fetch.oef.pb',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\nfipa.proto\x12\x0c\x66\x65tch.oef.pb\x1a\x0bquery.proto\"\xa1\x04\n\x04\x46ipa\x1a\x8d\x01\n\x03\x43\x66p\x12*\n\x05query\x18\x01 \x01(\x0b\x32\x19.fetch.oef.pb.Query.ModelH\x00\x12\x11\n\x07\x63ontent\x18\x02 \x01(\x0cH\x00\x12\x31\n\x07nothing\x18\x03 \x01(\x0b\x32\x1e.fetch.oef.pb.Fipa.Cfp.NothingH\x00\x1a\t\n\x07NothingB\t\n\x07payload\x1a\x9e\x01\n\x07Propose\x12\x39\n\tproposals\x18\x01 \x01(\x0b\x32$.fetch.oef.pb.Fipa.Propose.ProposalsH\x00\x12\x11\n\x07\x63ontent\x18\x02 \x01(\x0cH\x00\x1a:\n\tProposals\x12-\n\x07objects\x18\x01 \x03(\x0b\x32\x1c.fetch.oef.pb.Query.InstanceB\t\n\x07payload\x1a\x08\n\x06\x41\x63\x63\x65pt\x1a\t\n\x07\x44\x65\x63line\x1a\xd2\x01\n\x07Message\x12\x0e\n\x06target\x18\x01 \x02(\x05\x12%\n\x03\x63\x66p\x18\x02 \x01(\x0b\x32\x16.fetch.oef.pb.Fipa.CfpH\x00\x12-\n\x07propose\x18\x03 \x01(\x0b\x32\x1a.fetch.oef.pb.Fipa.ProposeH\x00\x12+\n\x06\x61\x63\x63\x65pt\x18\x04 \x01(\x0b\x32\x19.fetch.oef.pb.Fipa.AcceptH\x00\x12-\n\x07\x64\x65\x63line\x18\x05 \x01(\x0b\x32\x1a.fetch.oef.pb.Fipa.DeclineH\x00\x42\x05\n\x03msg')
  ,
  dependencies=[query__pb2.DESCRIPTOR,])




_FIPA_CFP_NOTHING = _descriptor.Descriptor(
  name='Nothing',
  full_name='fetch.oef.pb.Fipa.Cfp.Nothing',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=172,
  serialized_end=181,
)

_FIPA_CFP = _descriptor.Descriptor(
  name='Cfp',
  full_name='fetch.oef.pb.Fipa.Cfp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='query', full_name='fetch.oef.pb.Fipa.Cfp.query', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='content', full_name='fetch.oef.pb.Fipa.Cfp.content', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='nothing', full_name='fetch.oef.pb.Fipa.Cfp.nothing', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_FIPA_CFP_NOTHING, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='payload', full_name='fetch.oef.pb.Fipa.Cfp.payload',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=51,
  serialized_end=192,
)

_FIPA_PROPOSE_PROPOSALS = _descriptor.Descriptor(
  name='Proposals',
  full_name='fetch.oef.pb.Fipa.Propose.Proposals',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='objects', full_name='fetch.oef.pb.Fipa.Propose.Proposals.objects', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=284,
  serialized_end=342,
)

_FIPA_PROPOSE = _descriptor.Descriptor(
  name='Propose',
  full_name='fetch.oef.pb.Fipa.Propose',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='proposals', full_name='fetch.oef.pb.Fipa.Propose.proposals', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='content', full_name='fetch.oef.pb.Fipa.Propose.content', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_FIPA_PROPOSE_PROPOSALS, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='payload', full_name='fetch.oef.pb.Fipa.Propose.payload',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=195,
  serialized_end=353,
)

_FIPA_ACCEPT = _descriptor.Descriptor(
  name='Accept',
  full_name='fetch.oef.pb.Fipa.Accept',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=355,
  serialized_end=363,
)

_FIPA_DECLINE = _descriptor.Descriptor(
  name='Decline',
  full_name='fetch.oef.pb.Fipa.Decline',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=365,
  serialized_end=374,
)

_FIPA_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='fetch.oef.pb.Fipa.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='target', full_name='fetch.oef.pb.Fipa.Message.target', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cfp', full_name='fetch.oef.pb.Fipa.Message.cfp', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='propose', full_name='fetch.oef.pb.Fipa.Message.propose', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='accept', full_name='fetch.oef.pb.Fipa.Message.accept', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='decline', full_name='fetch.oef.pb.Fipa.Message.decline', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='msg', full_name='fetch.oef.pb.Fipa.Message.msg',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=377,
  serialized_end=587,
)

_FIPA = _descriptor.Descriptor(
  name='Fipa',
  full_name='fetch.oef.pb.Fipa',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[_FIPA_CFP, _FIPA_PROPOSE, _FIPA_ACCEPT, _FIPA_DECLINE, _FIPA_MESSAGE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=42,
  serialized_end=587,
)

_FIPA_CFP_NOTHING.containing_type = _FIPA_CFP
_FIPA_CFP.fields_by_name['query'].message_type = query__pb2._QUERY_MODEL
_FIPA_CFP.fields_by_name['nothing'].message_type = _FIPA_CFP_NOTHING
_FIPA_CFP.containing_type = _FIPA
_FIPA_CFP.oneofs_by_name['payload'].fields.append(
  _FIPA_CFP.fields_by_name['query'])
_FIPA_CFP.fields_by_name['query'].containing_oneof = _FIPA_CFP.oneofs_by_name['payload']
_FIPA_CFP.oneofs_by_name['payload'].fields.append(
  _FIPA_CFP.fields_by_name['content'])
_FIPA_CFP.fields_by_name['content'].containing_oneof = _FIPA_CFP.oneofs_by_name['payload']
_FIPA_CFP.oneofs_by_name['payload'].fields.append(
  _FIPA_CFP.fields_by_name['nothing'])
_FIPA_CFP.fields_by_name['nothing'].containing_oneof = _FIPA_CFP.oneofs_by_name['payload']
_FIPA_PROPOSE_PROPOSALS.fields_by_name['objects'].message_type = query__pb2._QUERY_INSTANCE
_FIPA_PROPOSE_PROPOSALS.containing_type = _FIPA_PROPOSE
_FIPA_PROPOSE.fields_by_name['proposals'].message_type = _FIPA_PROPOSE_PROPOSALS
_FIPA_PROPOSE.containing_type = _FIPA
_FIPA_PROPOSE.oneofs_by_name['payload'].fields.append(
  _FIPA_PROPOSE.fields_by_name['proposals'])
_FIPA_PROPOSE.fields_by_name['proposals'].containing_oneof = _FIPA_PROPOSE.oneofs_by_name['payload']
_FIPA_PROPOSE.oneofs_by_name['payload'].fields.append(
  _FIPA_PROPOSE.fields_by_name['content'])
_FIPA_PROPOSE.fields_by_name['content'].containing_oneof = _FIPA_PROPOSE.oneofs_by_name['payload']
_FIPA_ACCEPT.containing_type = _FIPA
_FIPA_DECLINE.containing_type = _FIPA
_FIPA_MESSAGE.fields_by_name['cfp'].message_type = _FIPA_CFP
_FIPA_MESSAGE.fields_by_name['propose'].message_type = _FIPA_PROPOSE
_FIPA_MESSAGE.fields_by_name['accept'].message_type = _FIPA_ACCEPT
_FIPA_MESSAGE.fields_by_name['decline'].message_type = _FIPA_DECLINE
_FIPA_MESSAGE.containing_type = _FIPA
_FIPA_MESSAGE.oneofs_by_name['msg'].fields.append(
  _FIPA_MESSAGE.fields_by_name['cfp'])
_FIPA_MESSAGE.fields_by_name['cfp'].containing_oneof = _FIPA_MESSAGE.oneofs_by_name['msg']
_FIPA_MESSAGE.oneofs_by_name['msg'].fields.append(
  _FIPA_MESSAGE.fields_by_name['propose'])
_FIPA_MESSAGE.fields_by_name['propose'].containing_oneof = _FIPA_MESSAGE.oneofs_by_name['msg']
_FIPA_MESSAGE.oneofs_by_name['msg'].fields.append(
  _FIPA_MESSAGE.fields_by_name['accept'])
_FIPA_MESSAGE.fields_by_name['accept'].containing_oneof = _FIPA_MESSAGE.oneofs_by_name['msg']
_FIPA_MESSAGE.oneofs_by_name['msg'].fields.append(
  _FIPA_MESSAGE.fields_by_name['decline'])
_FIPA_MESSAGE.fields_by_name['decline'].containing_oneof = _FIPA_MESSAGE.oneofs_by_name['msg']
DESCRIPTOR.message_types_by_name['Fipa'] = _FIPA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Fipa = _reflection.GeneratedProtocolMessageType('Fipa', (_message.Message,), dict(

  Cfp = _reflection.GeneratedProtocolMessageType('Cfp', (_message.Message,), dict(

    Nothing = _reflection.GeneratedProtocolMessageType('Nothing', (_message.Message,), dict(
      DESCRIPTOR = _FIPA_CFP_NOTHING,
      __module__ = 'fipa_pb2'
      # @@protoc_insertion_point(class_scope:fetch.oef.pb.Fipa.Cfp.Nothing)
      ))
    ,
    DESCRIPTOR = _FIPA_CFP,
    __module__ = 'fipa_pb2'
    # @@protoc_insertion_point(class_scope:fetch.oef.pb.Fipa.Cfp)
    ))
  ,

  Propose = _reflection.GeneratedProtocolMessageType('Propose', (_message.Message,), dict(

    Proposals = _reflection.GeneratedProtocolMessageType('Proposals', (_message.Message,), dict(
      DESCRIPTOR = _FIPA_PROPOSE_PROPOSALS,
      __module__ = 'fipa_pb2'
      # @@protoc_insertion_point(class_scope:fetch.oef.pb.Fipa.Propose.Proposals)
      ))
    ,
    DESCRIPTOR = _FIPA_PROPOSE,
    __module__ = 'fipa_pb2'
    # @@protoc_insertion_point(class_scope:fetch.oef.pb.Fipa.Propose)
    ))
  ,

  Accept = _reflection.GeneratedProtocolMessageType('Accept', (_message.Message,), dict(
    DESCRIPTOR = _FIPA_ACCEPT,
    __module__ = 'fipa_pb2'
    # @@protoc_insertion_point(class_scope:fetch.oef.pb.Fipa.Accept)
    ))
  ,

  Decline = _reflection.GeneratedProtocolMessageType('Decline', (_message.Message,), dict(
    DESCRIPTOR = _FIPA_DECLINE,
    __module__ = 'fipa_pb2'
    # @@protoc_insertion_point(class_scope:fetch.oef.pb.Fipa.Decline)
    ))
  ,

  Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
    DESCRIPTOR = _FIPA_MESSAGE,
    __module__ = 'fipa_pb2'
    # @@protoc_insertion_point(class_scope:fetch.oef.pb.Fipa.Message)
    ))
  ,
  DESCRIPTOR = _FIPA,
  __module__ = 'fipa_pb2'
  # @@protoc_insertion_point(class_scope:fetch.oef.pb.Fipa)
  ))
_sym_db.RegisterMessage(Fipa)
_sym_db.RegisterMessage(Fipa.Cfp)
_sym_db.RegisterMessage(Fipa.Cfp.Nothing)
_sym_db.RegisterMessage(Fipa.Propose)
_sym_db.RegisterMessage(Fipa.Propose.Proposals)
_sym_db.RegisterMessage(Fipa.Accept)
_sym_db.RegisterMessage(Fipa.Decline)
_sym_db.RegisterMessage(Fipa.Message)


# @@protoc_insertion_point(module_scope)
