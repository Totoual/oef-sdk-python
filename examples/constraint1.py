import sys
import os

PACKAGE_PARENT = '../oef_python'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import asyncio
from typing import List, Optional

from api import Description, AttributeSchema, AttributeInconsistencyException,\
        generate_schema, OEFProxy, DataModel, Query, Constraint, Range, In, NotIn, And, Or, CFP_TYPES

from google.protobuf import text_format

class Agent(object):
    def __init__(self, connection):
        self._connection = connection
        
    def onSearchResult(self, agents : List[str]) -> None:
        print("Agent.onSearchResult {0}".format(agents))
        self._results = agents
        
    def onMessage(self, origin: str, conversation_id : str, content : bytes):
        print("Received msg from {0} cid {1} content {2}".format(origin, conversation_id, content))
        
    def onCFP(self, origin: str, conversation_id : str, msg_id : int, target : int, query : CFP_TYPES):
        print("Received cfp from {0} cif {1} msgId {2} target {3} query [{4}]".format(origin, conversation_id, msg_id, target,
                                                                                    query))
    def onAccept(self, origin: str, conversation_id : str, msg_id : int, target : int):
        print("Received accept from {0} cif {1} msgId {2} target {3}".format(origin, conversation_id, msg_id, target))
    
if __name__ == "__main__":
    connection1 = OEFProxy("PythonAgent1", "127.0.0.1")
    connection2 = OEFProxy("PythonAgent2", "127.0.0.1")
    connection3 = OEFProxy("PythonAgent3", "127.0.0.1")
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(connection1.connect())
    event_loop.run_until_complete(connection2.connect())
    event_loop.run_until_complete(connection3.connect())
    car_model = DataModel("car", [AttributeSchema("manufacturer", str, True),
                                  AttributeSchema("colour", str, False),
                                  AttributeSchema("luxury", bool, True),
                                  AttributeSchema("year", int, True),
                                  AttributeSchema("price", float, True)])
    car_description1 = Description({"manufacturer": "Ferrari", "colour": "Aubergine", "luxury": True, "year": 2012, "price": 10000.0},
                                   car_model)
    car_description2 = Description({"manufacturer": "Lamborghini", "luxury": True, "year": 2015, "price": 20000.0},
                                   car_model)
    connection1.register_service(car_description1)
    connection2.register_service(car_description2)
#    query = Query([Constraint(AttributeSchema("year", int, True), Range((2000,2013)))])
#    query = Query([Constraint(AttributeSchema("price", float, True), Range((5000.,20000.)))])
#    query = Query([Constraint(AttributeSchema("manufacturer", str, True), Range(("A","K")))])
#    query = Query([Constraint(AttributeSchema("manufacturer", str, True), NotIn(["Lamborghini","Porsche"]))])
#    query = Query([Constraint(AttributeSchema("year", int, True), In([2000,2012]))])
    query = Query([Constraint(AttributeSchema("price", float, True), In([5000.,20000.]))])
#    query = Query([Constraint(AttributeSchema("luxury", bool, True), In([True]))])
    query_pb = query.to_query_pb()
    print(text_format.MessageToString(query_pb))
    query2 = Query.from_pb(query_pb)
    print(text_format.MessageToString(query2.to_pb()))
    and_ = And([Or([Range((2000,2013))])])
    print(text_format.MessageToString(and_.to_pb()))
    connection3.search_services(query)
    agent = Agent(connection3)
    event_loop.run_until_complete(connection3.loop(agent))
