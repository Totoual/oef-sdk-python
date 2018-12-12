#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.

"""
Weather client agent
~~~~~~~~~~~~~~~~~

This script belongs to the ``weather`` example of OEF Agent development, and implements the weather client agent.
It assumes that an instance of the OEF Node is running at ``127.0.0.1:3333``.

The script does the following:

1. Instantiate a ``WeatherClientAgent``
2. Connect the agent to the OEF Node.
3. Make a query on ``echo`` services via the ``search_services`` method.
4. Run the agent, waiting for messages from the OEF.


The class ``WeatherClientAgent`` define the behaviour of the weather client agent.

* when the agent receives a search result from the OEF (see ``on_search_result``), it sends an "hello" message to
  every agent found.
* once he receives a message (see ``on_message`` method), he stops.

Other methods (e.g. ``on_cfp``, ``on_error`` etc.) are omitted, since not needed.


"""

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

            # we send a query with no constraints, meaning "give me all the resources you can propose."
            query = Query([], WEATHER_DATA_MODEL)
            self.send_cfp(0, agent, query)

    def on_propose(self, origin: str, dialogue_id: int, msg_id: int, target: int, proposals: PROPOSE_TYPES):
        print("Received propose from {0} cif {1} msgId {2} target {3} proposals {4}"
              .format(origin, dialogue_id, msg_id, target, proposals))
        print("Price {0}".format(proposals[0].values["price"]))
        self.send_accept(dialogue_id, origin, msg_id + 1, msg_id)


if __name__ == "__main__":

    # create and connect the agent
    agent = WeatherClient("weather_client", oef_addr="127.0.0.1", oef_port=3333)
    agent.connect()

    # look for service agents registered as 'weather_station' that:
    # - provide measurements for temperature
    # - provide measurements for air pressure
    # - provide measurements for humidity
    query = Query([Constraint(TEMPERATURE_ATTR, Eq(True)),
                   Constraint(AIR_PRESSURE_ATTR, Eq(True)),
                   Constraint(HUMIDITY_ATTR, Eq(True))],
                  WEATHER_DATA_MODEL)

    agent.search_services(0, query)

    agent.run()
