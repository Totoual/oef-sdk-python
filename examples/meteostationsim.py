import sys
import os

PACKAGE_PARENT = '../oef_python'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import asyncio
from typing import List, Optional

from api import Description, AttributeSchema, AttributeInconsistencyException,\
        generate_schema, OEFProxy, DataModel, Query, CFP_TYPES

class Agent(object):
    def __init__(self, connection):
        self._connection = connection
        
    def onSearchResult(self, agents : List[str]) -> None:
        print("Agent.onSearchResult {0}".format(agents))

    def onMessage(self, origin: str, conversation_id : str, content : bytes):
        print("Received from {0} cid {1} content {2}".format(origin, conversation_id, content))
        if content == b'price':
            self._connection.send_message(conversation_id, origin, b'12.5')
        
    def onCFP(self, origin: str, conversation_id : str, msg_id : int, target : int, query : CFP_TYPES):
        print("Received cfp from {0} cif {1} msgId {2} target {3} query [{4}]".format(origin, conversation_id, msg_id, target,
                                                                                    query))
        proposal = Description({"price": 13}, DataModel("weather_data", [AttributeSchema("price", int, True)]))
        self._connection.send_propose(conversation_id, origin, [proposal] ,msg_id + 1, target + 1)

    def onAccept(self, origin: str, conversation_id : str, msg_id : int, target : int):
        print("Received accept from {0} cif {1} msgId {2} target {3}".format(origin, conversation_id, msg_id, target))
    
if __name__ == "__main__":
    connection = OEFProxy("PythonMeteoStation", "127.0.0.1")
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(connection.connect())
    station_model = DataModel("weather_data",
                              [AttributeSchema("wind_speed", bool, True), AttributeSchema("temperature", bool, True),
                               AttributeSchema("air_pressure", bool, True),AttributeSchema("humidity", bool, True)],
                              "All possible weather data.")
    station_description = Description({"wind_speed": True, "temperature": True, "air_pressure": True, "humidity": True},
                                      station_model)
    connection.register_service(station_description)
    print("loop")
    agent = Agent(connection)
    event_loop.run_until_complete(connection.loop(agent))
