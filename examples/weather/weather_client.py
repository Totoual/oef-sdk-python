# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from weather_schema import WEATHER_DATA_MODEL, TEMPERATURE_ATTR, AIR_PRESSURE_ATTR, HUMIDITY_ATTR
from oef.agents import OEFAgent

from typing import List
from oef.proxy import PROPOSE_TYPES
from oef.query import Eq, Constraint
from oef.query import Query


class WeatherClient(OEFAgent):

    def on_search_result(self, search_id: int, agents: List[str]):
        print("Agent found: {0}".format(agents))
        for agent in agents:
            print("Sending to agent {0}".format(agent))
            query = Query([Constraint(TEMPERATURE_ATTR, Eq(True)),
                           Constraint(AIR_PRESSURE_ATTR, Eq(True)),
                           Constraint(HUMIDITY_ATTR, Eq(True))],
                          WEATHER_DATA_MODEL)
            self.send_cfp(0, agent, query)

    def on_propose(self, origin: str, dialogue_id: int, msg_id: int, target: int, proposals: PROPOSE_TYPES):
        print("Received propose from {0} cif {1} msgId {2} target {3} proposals {4}"
              .format(origin, dialogue_id, msg_id, target, proposals))
        print("Price {0}".format(proposals[0]._values["price"]))
        self.send_accept(dialogue_id, origin, msg_id + 1, msg_id)


if __name__ == "__main__":
    agent = WeatherClient("weather_client", oef_addr="127.0.0.1", oef_port=3333)
    agent.connect()

    query = Query([Constraint(TEMPERATURE_ATTR, Eq(True)),
                   Constraint(AIR_PRESSURE_ATTR, Eq(True)),
                   Constraint(HUMIDITY_ATTR, Eq(True))],
                  WEATHER_DATA_MODEL)

    agent.search_services(0, query)

    agent.run()
