#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.

"""
The local counterpart implementation of the weather example.
"""
import asyncio
from typing import List

from examples.weather.weather_schema import WEATHER_DATA_MODEL, TEMPERATURE_ATTR, AIR_PRESSURE_ATTR, HUMIDITY_ATTR
from oef.agents import LocalAgent
from oef.proxy import CFP_TYPES, OEFLocalProxy
from oef.proxy import PROPOSE_TYPES
from oef.query import Eq, Constraint
from oef.query import Query
from oef.schema import Description


class WeatherClient(LocalAgent):

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


class WeatherStation(LocalAgent):
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

    local_node = OEFLocalProxy.LocalNode()

    client = WeatherClient("weather_client", local_node)
    server = WeatherStation("weather_station", local_node)
    client.connect()
    server.connect()

    server.register_service(server.weather_service_description)

    query = Query([Constraint(TEMPERATURE_ATTR, Eq(True)),
                   Constraint(AIR_PRESSURE_ATTR, Eq(True)),
                   Constraint(HUMIDITY_ATTR, Eq(True))],
                  WEATHER_DATA_MODEL)

    client.on_search_result(0, ["weather_station"])

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            client.async_run(),
            server.async_run(),
            local_node.run()))
    finally:
        local_node.stop()
        client.stop()
        server.stop()
