import sys
import os

from oef.agents import OEFAgent
from oef.proxy import CFP_TYPES
from oef.query import Range, And, Or, Constraint
from oef.schema import AttributeSchema, DataModel, Description
from oef.query import Query

PACKAGE_PARENT = '../oef'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from typing import List

from google.protobuf import text_format

class Agent(OEFAgent):
    def __init__(self, public_key: str, oef_addr: str, oef_port: int = 3333) -> None:
        super().__init__(public_key, oef_addr, oef_port)
        
    def on_search_result(self, agents: List[str]):
        print("Agent.onSearchResult {0}".format(agents))
        self._results = agents
        
    def on_message(self, origin: str, conversation_id: str, content: bytes):
        print("Received msg from {0} cid {1} content {2}".format(origin, conversation_id, content))
        
    def on_cfp(self, origin: str,
            conversation_id: str,
            fipa_message_id: int,
            fipa_target: int,
            query: CFP_TYPES):
        print("Received cfp from {0} cif {1} msgId {2} target {3} query [{4}]".format(origin, conversation_id, msg_id, target,
                                                                                    query))
    def on_accept(self, origin: str,
            conversation_id: str,
            fipa_message_id: int,
            fipa_target: int,):
        print("Received accept from {0} cif {1} msgId {2} target {3}".format(origin, conversation_id, msg_id, target))
    
if __name__ == "__main__":
    agent1 = Agent("PythonAgent1", "127.0.0.1")
    agent2 = Agent("PythonAgent2", "127.0.0.1")
    agent3 = Agent("PythonAgent3", "127.0.0.1")

    agent1.connect()
    agent2.connect()
    agent3.connect()

    car_model = DataModel("car", [AttributeSchema("manufacturer", str, True),
                                  AttributeSchema("colour", str, False),
                                  AttributeSchema("luxury", bool, True),
                                  AttributeSchema("year", int, True),
                                  AttributeSchema("price", float, True)])
    car_description1 = Description({"manufacturer": "Ferrari", "colour": "Aubergine", "luxury": True, "year": 2012, "price": 10000.0},
                                   car_model)
    car_description2 = Description({"manufacturer": "Lamborghini", "luxury": True, "year": 2015, "price": 20000.0},
                                   car_model)
    agent1.register_service(car_description1)
    agent2.register_service(car_description2)
#    query = Query([Constraint(AttributeSchema("year", int, True), Range((2000,2013)))])
#    query = Query([Constraint(AttributeSchema("price", float, True), Range((5000.,20000.)))])
#    query = Query([Constraint(AttributeSchema("manufacturer", str, True), Range(("A","K")))])
#    query = Query([Constraint(AttributeSchema("manufacturer", str, True), NotIn(["Lamborghini","Porsche"]))])
#    query = Query([Constraint(AttributeSchema("year", int, True), In([2000,2012]))])
#    query = Query([Constraint(AttributeSchema("price", float, True), In([5000.,20000.]))])
#    query = Query([Constraint(AttributeSchema("luxury", bool, True), In([True]))])
    query = Query([Constraint(AttributeSchema("luxury", bool, True), And([Or([Range((2000, 2013))])]))])
    query_pb = query.to_pb()
    print(text_format.MessageToString(query_pb))
    query2 = Query.from_pb(query_pb)
    print(text_format.MessageToString(query2.to_search_pb()))
    and_ = And([Or([Range((2000,2013))])])
    # agent3.search_services(query)
    agent3.search_services(Query([]))
    agent3.run()
