# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from examples.weather.weather_schema import WEATHER_DATA_MODEL
from oef.agents import OEFAgent
from oef.proxy import CFP_TYPES
from oef.schema import Description


class WeatherStation(OEFAgent):

    weather_service_description = Description(
        {
            "wind_speed": True,
            "temperature": True,
            "air_pressure": True,
            "humidity": True,
            "price": 50
        },
        WEATHER_DATA_MODEL
    )

    def on_cfp(self,
               origin: str,
               dialogue_id: int,
               msg_id: int,
               target: int,
               query: CFP_TYPES):
        print("Received cfp from {0} cif {1} msgId {2} target {3} query [{4}]"
              .format(origin, dialogue_id, msg_id, target, query))

        # prepare a propose
        proposal = self.weather_service_description
        self.send_propose(dialogue_id, origin, [proposal], msg_id + 1, target + 1)

    def on_accept(self,
                  origin: str,
                  dialogue_id: int,
                  msg_id: int,
                  target: int):
        print("Received accept from {0} cif {1} msgId {2} target {3}"
              .format(origin, dialogue_id, msg_id, target))


if __name__ == "__main__":
    agent = WeatherStation("weather_station", oef_addr="127.0.0.1", oef_port=3333)
    agent.connect()
    agent.register_service(agent.weather_service_description)
    agent.run()
