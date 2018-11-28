from oef.agents import OEFAgent

from typing import List
from oef.api import AttributeSchema, DataModel, Eq, Query, Constraint, PROPOSE_TYPES


class WeatherClient(OEFAgent):

    def on_search_result(self, agents: List[str]):
        print("Agent.onSearchResult {0}".format(agents))
        for agent in agents:
            print("Sending to agent {0}".format(agent))
            station_model = DataModel("weather_data",
                                      [AttributeSchema("wind_speed", bool, True),
                                       AttributeSchema("temperature", bool, True),
                                       AttributeSchema("air_pressure", bool, True),
                                       AttributeSchema("humidity", bool, True)],
                                      "All possible weather data.")
            query = Query([Constraint(AttributeSchema("temperature", bool, True), Eq(True)),
                           Constraint(AttributeSchema("air_pressure", bool, True), Eq(True)),
                           Constraint(AttributeSchema("humidity", bool, True), Eq(True))],
                          station_model)
            self._connection.send_cfp("1", agent, query)

    def on_propose(self, origin: str, conversation_id: str, msg_id: int, target: int, proposals: PROPOSE_TYPES):
        print("Received propose from {0} cif {1} msgId {2} target {3} proposals {4}".format(origin, conversation_id, msg_id, target,
                                                                                    proposals))
        print("Price {0}".format(proposals[0]._values["price"]))
        self._connection.send_accept(conversation_id, origin, msg_id + 1, msg_id)


if __name__ == "__main__":
    station_model = DataModel("weather_data",
                              [AttributeSchema("wind_speed", bool, True), AttributeSchema("temperature", bool, True),
                               AttributeSchema("air_pressure", bool, True),AttributeSchema("humidity", bool, True)],
                              "All possible weather data.")
    query = Query([Constraint(AttributeSchema("temperature", bool, True), Eq(True)),
                   Constraint(AttributeSchema("air_pressure", bool, True), Eq(True)),
                   Constraint(AttributeSchema("humidity", bool, True), Eq(True))],
                  station_model)

    agent = WeatherClient("weather_client", oef_addr="127.0.0.1", oef_port=3333)
    agent.connect()
    agent.search_services(query)

    agent.run()
