import sys
import os

from oef.agents import OEFAgent

PACKAGE_PARENT = '../oef'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from typing import List

from oef.api import Description, AttributeSchema, AttributeInconsistencyException,\
        generate_schema, OEFProxy, DataModel, Eq, Query, Constraint, PROPOSE_TYPES

class Agent(OEFAgent):

    def on_search_result(self, agents: List[str]):
        print("Agent.onSearchResult {0}".format(agents))
        for agent in agents:
            print("Sending to agent {0}".format(agent))
            station_model = DataModel("weather_data",
                                      [AttributeSchema("wind_speed", bool, True), AttributeSchema("temperature", bool, True),
                                       AttributeSchema("air_pressure", bool, True),AttributeSchema("humidity", bool, True)],
                                      "All possible weather data.")
            query = Query([Constraint(AttributeSchema("temperature", bool, True), Eq(True)),
                           Constraint(AttributeSchema("air_pressure", bool, True), Eq(True)),
                           Constraint(AttributeSchema("humidity", bool, True), Eq(True))],
                          station_model)
            self._connection.send_cfp("1", agent, query)

    def on_message(self, origin: str, conversation_id: str, content: bytes):
        print("Received from {0} cid {1} content {2}".format(origin, conversation_id, content))

    def on_propose(self, origin: str, conversation_id : str, msg_id : int, target : int, proposals : PROPOSE_TYPES):
        print("Received propose from {0} cif {1} msgId {2} target {3} proposals {4}".format(origin, conversation_id, msg_id, target,
                                                                                    proposals))
        print("Price {0}".format(proposals[0]._values["price"]))
        self._connection.send_accept(conversation_id, origin, msg_id + 1, msg_id)
        
if __name__ == "__main__":
    print("datamodel")
    station_model = DataModel("weather_data",
                              [AttributeSchema("wind_speed", bool, True), AttributeSchema("temperature", bool, True),
                               AttributeSchema("air_pressure", bool, True),AttributeSchema("humidity", bool, True)],
                              "All possible weather data.")
    query = Query([Constraint(AttributeSchema("temperature", bool, True), Eq(True)),
                   Constraint(AttributeSchema("air_pressure", bool, True), Eq(True)),
                   Constraint(AttributeSchema("humidity", bool, True), Eq(True))],
                  station_model)
    agent = Agent("PythonMeteoClient", "127.0.0.1")
    agent.connect()
    agent.search_services(query)
    print("loop")
    agent.run()
