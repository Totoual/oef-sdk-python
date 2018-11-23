import sys
import os

from oef.agents import OEFAgent
from oef.api import CFP_TYPES, Description, DataModel, AttributeSchema

PACKAGE_PARENT = '../oef'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from typing import List

class Agent(OEFAgent):

    def on_search_result(self, agents : List[str]) -> None:
        print("Agent.on_search_result {0}".format(agents))

    def on_message(self, origin: str, conversation_id : str, content : bytes):
        print("Received from {0} cid {1} content {2}".format(origin, conversation_id, content))
        if content == b'price':
            self._connection.send_message(conversation_id, origin, b'12.5')
        
    def on_cfp(self, origin: str, conversation_id : str, msg_id : int, target : int, query : CFP_TYPES):
        print("Received cfp from {0} cif {1} msgId {2} target {3} query [{4}]".format(origin, conversation_id, msg_id, target,
                                                                                    query))
        proposal = Description({"price": 13}, DataModel("weather_data", [AttributeSchema("price", int, True)]))
        self._connection.send_propose(conversation_id, origin, [proposal] ,msg_id + 1, target + 1)

    def on_accept(self, origin: str, conversation_id : str, msg_id : int, target : int):
        print("Received accept from {0} cif {1} msgId {2} target {3}".format(origin, conversation_id, msg_id, target))
    
if __name__ == "__main__":
    station_model = DataModel("weather_data",
                              [AttributeSchema("wind_speed", bool, True), AttributeSchema("temperature", bool, True),
                               AttributeSchema("air_pressure", bool, True),AttributeSchema("humidity", bool, True)],
                              "All possible weather data.")
    station_description = Description({"wind_speed": True, "temperature": True, "air_pressure": True, "humidity": True},
                                      station_model)
    agent = Agent("PythonMeteoStation", "127.0.0.1")
    agent.connect()
    agent.register_service(station_description)
    print("loop")
    agent.run()
