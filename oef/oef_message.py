# vim: set number autoindent tabstop=2 expandtab :
# Company: FETCH.ai
# Author: Lokman Rahmani
# Creation: 26/09/18
#
# This file implements messages creations needed for agents to
#  be able to communicate with OEF core
# It basically defines functions  wrappers for proto buffers
#  messages allowing to create a message by passing its fields as arguments
#  with type checking
#
# It follows these rules:
#   - naming convention: make<ParentMessage><MessageName>() to match protos
#     - e.g. def makeQueryConstraintConstraintType(constraint)
#     Conflict can happen when MessageName is two worl with no spaces first
#      letter capital
#   - optinal fields are implemted as optional argument, and it will be set
#     only if a valid value is passed
#     - e.g. def makeQueryModel(constraints, model=None)
#   - EnumTypes are implemented as str arguments with value checking
#     - Note that it is hard to check enum types as they are implemented as
#        ints in python ...
#     - e.g. def makeQueryRelationOperator(operator_name)
#   - oneof-only messages: only one argument (2 atmost) is needed. 
#     The choise of the field is selected automaticaly based on the type of
#      arguments passed to the function with err checking
#     - e.g. def makeQueryValue(value)
#     - If the oneof message has mutliple fields with the same type, a 
#        a second paramter is needed implemented as a string to specify
#        which field to set, with value checking
#       - e.g. def makeEnvelope(payload,field=None)
#
# Note: I am no python expert, any comments/suggestions are welcome :)


import oef.agent_pb2 as agent_pb2
import oef.query_pb2 as query_pb2
import oef.fipa_pb2 as fipa_pb2

# NOT used yet - TODO
# parmeters type check
def typeCheckParam(param, expected_type):
  if not isinstance(param, expected_type):
    raise TypeError(
      'Parameter <param name here> must be instance of class '
      '%s got %s' % (param.__class__, expected_type.__name__))

# create a new Agent.Server.ID()
# Used in: TODO
def makeAgentServerID(pubkey):
  if not isinstance(pubkey, str):
    raise TypeError(
      'Parameter pubkey must be instance of class '
      '%s got %s' % ("".__class__, type(pubkey).__name__))
  pb_id = agent_pb2.Agent.Server.ID()
  pb_id.public_key = pubkey
  return pb_id

# create a new Server.Phrase
# Used in: TODO
def makeServerPhrase(handshake_phrase):
  if not isinstance(handshake_phrase, str):
    raise TypeError(
      'Parameter handshake_phrase must be instance of class '
      '%s got %s' % ("".__class__, type(handshake_phrase).__name__))
  phrase = agent_pb2.Server.Phrase()
  phrase.phrase = handshake_phrase
  return phrase

# create a new Sever.Answer
# Used in: TODO
def makeAgentServerAnswer(answer_phrase):
  if not isinstance(answer_phrase, str):
    raise TypeError(
      'Parameter answer_phrase must be instance of class '
      '%s got %s' % ("".__class__, type(answer_phrase).__name__))
  pb_answer = agent_pb2.Agent.Server.Answer()
  pb_answer.answer = answer_phrase
  return pb_answer

# create a new Server.Connected
# Used in: TODO
def makeServerConnected(status):
  if not isinstance(status, bool):
    raise TypeError(
      'Parameter status must be instance of class '
      '%s got %s' % (True.__class__, type(status).__name__))
  status_pb = agent_pb2.Server.Connected()
  status_pb.status = status
  return status_pb

# create a new Query.Attribute.Type
# Used in: TODO
def makeQueryAttributeType(type_name):
  if not isinstance(type_name, str):
    raise TypeError(
      'Parameter type_name must be instance of class '
      '%s got %s' % ("".__class__, type(type_name).__name__))
  if type_name == "BOOL":
    return query_pb2.Query.Attribute.BOOL
  elif type_name == "INT":
    return query_pb2.Query.Attribute.INT
  elif type_name == "FLOAT":
    return query_pb2.Query.Attribute.FLOAT
  elif type_name == "STRING":
    return query_pb2.Query.Attribute.STRING
  else:
    return None
  



# create a new Query.Attribute
# Used in: TODO
def makeQueryAttribute(name, attr_type, is_required, description=None):
  if(not isinstance(name, str) or
     not isinstance(attr_type, type(query_pb2.Query.Attribute.BOOL)) or
     not isinstance(is_required, bool) or
    (not isinstance(description, str) and description is not None)):
    raise TypeError(
      'Parameters (name, attr_type, is_required, [optional]description)'
      'must be instances of classes '
      '<%s,%s,%s,[op]%s> got <%s,%s,%s,%s>' % 
      ("".__class__, type(query_pb2.Query.Attribute.BOOL).__name__, 
      True.__class__, "".__class__,
      type(name).__name__,type(attr_type).__name__,
      type(is_required).__name__,type(description).__name__ ))
  attrib = query_pb2.Query.Attribute()
  attrib.name = name
  attrib.type = attr_type
  attrib.required = is_required
  if description is not None:
    attrib.description = description

  return attrib

# create a new Query.DataModel
# Used in: TODO
def makeQueryDataModel(name, attributes, description=None):
  if(not isinstance(name, str) or
    (not isinstance(attributes, type([])) or len(attributes) <= 0 or
         not isinstance(attributes[0],type(query_pb2.Query.Attribute()))) or
    (not isinstance(description, str) and description is not None)):
    raise TypeError(
      'Parameters (name, attributes, [optional]description)'
      'must be instances of classes '
      '<%s,%s[%s],[op]%s> got <%s,%s,%s>' % 
      ("".__class__, type([]).__name__, 
      type(query_pb2.Query.Attribute()).__name__, "".__class__,
      type(name).__name__,type(attributes).__name__,
      type(description).__name__ ))
  model = query_pb2.Query.DataModel()
  model.name = name
  model.attributes.extend(attributes)
  if description is not None:
    model.description = description
  return model
  
# create a new Query.Value
# Used in: TODO
def makeQueryValue(value):
  if(not isinstance(value, bool) and
     not isinstance(value, int) and
     not isinstance(value, float) and 
     not isinstance(value, str)):
    raise TypeError(
      'Parameter value must be instance of one of following classes '
      '<%s,%s,%s,%s> got %s' % 
      (bool.__name__, int.__name__, float.__name__, str.__name__,
      type(value).__name__ ))
  query_value = query_pb2.Query.Value()
  if isinstance(value, bool):
    query_value.b = value
  elif isinstance(value, int):
    query_value.i = value
  elif isinstance(value, float):
    query_value.f = value
  elif isinstance(value, str):
    query_value.s = value

  return query_value

# create a new Query.Relation.Operator
# used in: TODO
def makeQueryRelationOperator(operator_name):
  if not isinstance(operator_name, str):
    raise TypeError(
      'Parameter operator_name must be instance of class '
      '%s got %s' % ("".__class__, type(operator_name).__name__))
  if operator_name == "EQ":
    return query_pb2.Query.Relation.EQ
  elif operator_name == "LT":
    return query_pb2.Query.Relation.LT
  elif operator_name == "LTEQ":
    return query_pb2.Query.Relation.LTEQ
  elif operator_name == "GT":
    return query_pb2.Query.Relation.GT
  elif operator_name == "GTEQ":
    return query_pb2.Query.Relation.GTEQ
  elif operator_name == "NOTEQ":
    return query_pb2.Query.Relation.NOTEQ
  else:
    return None

# create a new Query.Relation
# Used in: TODO
# TODO TOFIX How to test enum types?
def makeQueryRelation(op, val):
  if(not isinstance(op, type(query_pb2.Query.Relation.EQ)) or
     not isinstance(val, query_pb2.Query.Value)):
    raise TypeError(
      'Parameters (op, val) must be instances of classes '
      '<[enum]%s,%s> got <%s,%s>' % 
      (type(query_pb2.Query.Relation.EQ), 
       query_pb2.Query.Value, type(op).__name__, type(val).__name__))
  relation = query_pb2.Query.Relation()
  relation.op = op
  relation.val.CopyFrom(val)

  return relation

# create a new Query.Constraint.ConstraintType
# Used in: TODO
# TODO TOFIX Change ConstraintType to Type
def makeQueryConstraintConstraintType(constraint):
  if(not isinstance(constraint, 
      query_pb2.Query.Constraint.ConstraintType.Or) and
     not isinstance(constraint, 
      query_pb2.Query.Constraint.ConstraintType.And) and
     not isinstance(constraint, query_pb2.Query.Set) and
     not isinstance(constraint, query_pb2.Query.Range) and
     not isinstance(constraint, query_pb2.Query.Relation)):
    raise TypeError(
      'Parameter value must be instance of one of following classes '
      '<%s,%s,%s,%s,%s> got %s' % 
      (query_pb2.Query.Constraint.ConstraintType.Or.__name__, 
       query_pb2.Query.Constraint.ConstraintType.And.__name__, 
       query_pb2.Query.Set.__name__,query_pb2.Query.Range.__name__,
       query_pb2.Query.Relation.__name__,
       type(constraint).__name__ ))
  constraint_type = query_pb2.Query.Constraint.ConstraintType()
  if isinstance(constraint, 
      query_pb2.Query.Constraint.ConstraintType.Or):
    constraint_type.or_.CopyFrom(constraint)
  elif isinstance(constraint, 
      query_pb2.Query.Constraint.ConstraintType.And):
    constraint_type.and_.CopyFrom(constraint)
  elif isinstance(constraint, query_pb2.Query.Set):
    constraint_type.set.CopyFrom(constraint)
  elif isinstance(constraint, query_pb2.Query.Range):
    constraint_type.range.CopyFrom(constraint)
  elif isinstance(constraint, query_pb2.Query.Relation):
    constraint_type.rel.CopyFrom(constraint)

  return constraint_type


# create a new Query.Constraint
# Used in: TODO
def makeQueryConstraint(attribute, constraint_type):
  if(not isinstance(attribute, query_pb2.Query.Attribute) or
     not isinstance(constraint_type, 
          query_pb2.Query.Constraint.ConstraintType)):
    raise TypeError(
      'Parameters (attribute, constraint_type) must be instances of classes '
      '<%s,%s> got <%s,%s>' % 
      (query_pb2.Query.Attribute, query_pb2.Query.Constraint.ConstraintType,
       type(attribute).__name__, type(constraint_type).__name__))
  constraint = query_pb2.Query.Constraint()
  constraint.attribute.CopyFrom(attribute)
  constraint.constraint.CopyFrom(constraint_type)

  return constraint


# create new Query.Model
# Used in: TODO
def makeQueryModel(constraints, model=None):
  if(not isinstance(constraints, list) or len(constraints) <= 0 or 
      not isinstance(constraints[0], query_pb2.Query.Constraint) or
     (model is not None and not isinstance(model,query_pb2.Query.DataModel))):
    raise TypeError(
      'Parameters (constraints, [optional]model)'
      'must be instances of classes '
      '<%s[%s],[op]%s> got <%s[%],%s>' % 
      (list.__name__, query_pb2.Query.Constraint, query_pb2.Query.DataModel, 
      type(constraints).__name__, type(model).__name__))
  query = query_pb2.Query.Model()
  query.constraints.extend(constraints)
  if model is not None:
    query.model.CopyFrom(model)

  return query

# create new AgentSearch
# Used in: TODO
def makeAgentSearch(query):
  if not isinstance(query, query_pb2.Query.Model):
    raise TypeError(
      'Parameters query  must be instance of classe '
      '<%s> got <%s>' % 
      (query_pb2.Query.Model, type(query).__name__))
  agent_search = agent_pb2.AgentSearch()
  agent_search.query.CopyFrom(query)
  
  return agent_search
 
# create a new Envelope
def makeEnvelope(payload,field=None):
  if(not isinstance(payload, agent_pb2.Agent.Message) and
     not isinstance(payload, agent_pb2.AgentDescription) and
     not isinstance(payload, agent_pb2.AgentSearch) or
     (field is not None and not isinstance(field,str))):
    raise TypeError(
      'Parameter payload must be instance of one of following classes '
      '<%s,%s,%s,%s,%s> got %s.'
      'Parameter [optional] field must be instance of %s got %s' % 
      (agent_pb2.Agent.Message.__name__, 
       agent_pb2.AgentDescription.__name__, 
       agent_pb2.AgentSearch.__name__,
       type(payload).__name__ ,
       str, type(field).__name__))
  envelope = agent_pb2.Envelope()
  if isinstance(payload, agent_pb2.Agent.Message): 
    envelope.message.CopyFrom(payload)
  elif isinstance(payload, agent_pb2.AgentDescription):
    fields = ["register","unregister","description"]
    if field is None or not field in fields:
      # I am abusing typeError here
      raise TypeError(
        'Parameter field need to be one of values %s for payload %s' %
        (fields,agent_pb2.AgentDescription))
    if field == fields[0]:
      envelope.register.CopyFrom(payload)
    if field == fields[1]:
      envelope.unregister.CopyFrom(payload)
    if field == fields[2]:
      envelope.description.CopyFrom(payload)
    # there should be no else
  elif isinstance(payload, agent_pb2.AgentSearch):
    fields = ["query","search"]
    if field is None or not field in fields:
      # I am abusing typeError here
      raise TypeError(
        'Parameter field need to be one of values %s for payload %s' %
        (fields,agent_pb2.AgentSearch))
    if field == fields[0]:
      envelope.query.CopyFrom(payload)
    if field == fields[1]:
      envelope.search.CopyFrom(payload)
    
  return envelope

# create a Query.KeyValue
# Used in: TODO
def makeQueryKeyValue(key,value):
  if(not isinstance(key, str) or 
     (not isinstance(value, bool)  and not isinstance(value, int) and
      not isinstance(value, float) and not isinstance(value, str))):
    raise TypeError(
      'Parameters (key, value)'
      'must be instances of classes '
      '<%s,%s|%s|%s|%s> got <%s,%s>' % 
      (str, bool, int, float, str,
       type(key).__name__, type(value).__name__))
  
  key_val = query_pb2.Query.KeyValue()
  key_val.key = key
  # TOFIX a shortcut, creating Value within KeyValue 
  val = query_pb2.Query.Value()
  if isinstance(value, bool):
    val.b = value
  elif isinstance(value, int):
    val.i = value
  elif isinstance(value, float):
    val.f = value
  elif isinstance(value, str):
    val.s = value
  key_val.value.CopyFrom(val)

  return key_val

# create a Query.StringPair
# Used in; TODO
def makeQueryStringPair(first,second):
  if(not isinstance(first, str) or 
     not isinstance(second, str)):
    raise TypeError(
      'Parameters (first, second)'
      'must be instances of classes '
      '<%s,%s> got <%s,%s>' % 
      (str, str, type(first).__name__, type(second).__name__))
  str_pair = query_pb2.Query.StringPair()
  str_pair.first = first
  str_pair.second = second

  return str_pair

# create Query.Instance
# Used in: TODO
def makeQueryInstance(model,values):
  if(not isinstance(model, query_pb2.Query.DataModel) or 
     not isinstance(values, list) or len(values) <= 0 or 
      not isinstance(values[0], query_pb2.Query.KeyValue)):
    raise TypeError(
      'Parameters (model, values)'
      'must be instances of classes '
      '<%s,%s[%s]> got <%s,%s>' % 
      (query_pb2.Query.DataModel, list, query_pb2.Query.KeyValue.__name__,
       type(model).__name__, type(values).__name__))
  instance = query_pb2.Query.Instance()
  instance.model.CopyFrom(model)
  instance.values.extend(values)

  return instance

# create AgentDescription
# Used in: TODO
def makeAgentDescription(description):
  if not isinstance(description, query_pb2.Query.Instance): 
    raise TypeError(
      'Parameter description must be instance of class '
      '<%s> got <%s>' % 
      (query_pb2.Query.Instance, type(description).__name__))
  agent_desc = agent_pb2.AgentDescription()
  agent_desc.description.CopyFrom(description)

  return agent_desc

# create AgentMessage from binary 
# Used in:
def decodeServerAgentMessage(data):
  if not isinstance(data, bytes): 
    raise TypeError(
      'Parameter data must be instance of class '
      '<%s> got <%s>' % 
      (bytes, type(data).__name__))
  agent_msg = agent_pb2.Server.AgentMessage()
  agent_msg.ParseFromString(data)
  return agent_msg

# create Server.SearchResult from binary
# Used in:
def decodeServerSearchResult(data):
  if not isinstance(data, bytes):
    raise TypeError(
      'Parameter data must be instance of class'
      '<%s> got <%s>' %
      (bytes, type(data).__name__))
  query_answer = agent_pb2.Server.SearchResult()
  query_answer.ParseFromString(data)
  return query_answer

# create Agent.Message
def makeAgentMessage(cid, destination, content):
  if(not isinstance(cid, str) or 
     not isinstance(destination, str) or 
     (not isinstance(content, bytes) and 
      not isinstance(content, fipa_pb2.Fipa.Message))):
    raise TypeError(
      'Parameters (cid, destination, content)'
      'must be instances of classes '
      '<%s,%s,%s|%s> got <%s,%s,%s>' % 
      (str, str, bytes, fipa_pb2.Fipa.Message.__name__,type(cid).__name__, 
       type(destination).__name__, type(content).__name__))
  message = agent_pb2.Agent.Message()
  message.conversation_id = cid
  message.destination = destination
  if isinstance(content, bytes):
    message.content = content
  if isinstance(content, fipa_pb2.Fipa.Message):
    message.fipa.CopyFrom(content)

  return message

# create a new Boolean
# Used in:
def makeBoolean(status):
  if not isinstance(status, bool):
    raise TypeError(
      'Parameter status must be instance of class '
      '%s got %s' % (bool, type(status).__name__))
  boolean = agent_pb2.Boolean()
  boolean.status = status
  return boolean

# create a new Data from binary
def decodeData(data):
  if not isinstance(data, bytes):
    raise TypeError(
      'Parameter data must be instance of class'
      '<%s> got <%s>' %
      (bytes, type(data).__name__))
  data_ = agent_pb2.Data()
  data_.ParseFromString(data)
  return data_

# create a new Data 
def makeData(name, dtype, values):
  if(not isinstance(name, str) or
     not isinstance(dtype, str) or
     not isinstance(values, list) or len(values)<= 0 or 
      not isinstance(values[0],str)):
    raise TypeError(
      'Parameters (name,dtype,values) must be of instance of class'
      '<%s,%s,%s[%s]> got <%s,%s,%s>' %
      (str,str,list,str,type(name).__name__,type(dtype).__name__,
       type(values).__name__))
  data = agent_pb2.Data()
  data.name = name
  data.type = dtype
  data.values.extend(values)
  
  return data

def makeDataEmpty():
  data = agent_pb2.Data()
  return data

# create a new Boolean from binary
# Used in:
def decodeBoolean(data):
  if not isinstance(data, bytes):
    raise TypeError(
      'Parameter data must be instance of class '
      '%s got %s' % (bytes, type(data).__name__))
  boolean = agent_pb2.Boolean()
  boolean.ParseFromString(data)
  return boolean

