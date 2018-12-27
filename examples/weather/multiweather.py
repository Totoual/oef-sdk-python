# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
import asyncio
import uuid
from typing import List

from oef.proxy import OEFNetworkProxy

from oef import agent_pb2
from oef.dialogue import SingleDialogue, DialogueAgent
from oef.query import Query

from examples.weather.weather_schema import WEATHER_DATA_MODEL
from oef.schema import Description


from oef.messages import PROPOSE_TYPES, CFP_TYPES

from oef.agents import OEFAgent, Agent


class WeatherClient(DialogueAgent):
    """Class that implements the behavior of the weather client."""

    def on_error(self, operation: agent_pb2.Server.AgentMessage.Error.Operation, dialogue_id: int, message_id: int):
        pass

    def on_new_cfp(self):
        pass

    def on_new_message(self):
        pass

    def on_connection_error(self):
        pass

    def on_search_result(self, search_id: int, agents: List[str]):
        """For every agent returned in the service search, send a CFP to obtain resources from them."""
        print("Agent found: {0}".format(agents))
        for dialogue_id, agent in enumerate(agents):
            print("Sending to agent {0}".format(agent))
            # we send a query with no constraints, meaning "give me all the resources you can propose."
            query = Query([])

            self.send_cfp(dialogue_id, agent, query)
            new_dialogue = WeatherClientDialogue(self, agent, dialogue_id, True)
            self.register_dialogue(new_dialogue)


class WeatherClientDialogue(SingleDialogue):
    def on_error(self):
        pass

    def on_propose(self, origin: str, dialogue_id: int, msg_id: int, target: int, proposals: PROPOSE_TYPES):
        """When we receive a Propose message, answer with an Accept."""
        print("Received propose from agent {0}".format(origin))
        for i, p in enumerate(proposals):
            print("Proposal {}: {}".format(i, p.values))
        print("Accepting Propose.")
        self.agent.send_accept(dialogue_id, origin, msg_id + 1, msg_id)

    def on_message(self, origin: str,
                   dialogue_id: int,
                   content: bytes):
        """Extract and print data from incoming (simple) messages."""
        key, value = content.decode().split(":")
        print("Received measurement from {}: {}={}".format(origin, key, float(value)))

    def on_cfp(self, origin: str, dialogue_id: int, msg_id: int, target: int, query: CFP_TYPES) -> None:
        pass

    def on_accept(self, origin: str, dialogue_id: int, msg_id: int, target: int) -> None:
        pass

    def on_decline(self, origin: str, dialogue_id: int, msg_id: int, target: int) -> None:
        pass


class WeatherStation(Agent):
    """Class that implements the behaviour of the weather station."""

    weather_service_description = Description(
        {
            "wind_speed": False,
            "temperature": True,
            "air_pressure": True,
            "humidity": True,
        },
        WEATHER_DATA_MODEL
    )

    def on_cfp(self, origin: str,
               dialogue_id: int,
               msg_id: int,
               target: int,
               query: CFP_TYPES):
        """Send a simple Propose to the sender of the CFP."""
        print("Received CFP from {0}".format(origin))

        # prepare the proposal with a given price.
        proposal = Description({"price": 50})
        self.send_propose(dialogue_id, origin, [proposal], msg_id + 1, target + 1)

    def on_accept(self, origin: str,
                  dialogue_id: int,
                  msg_id: int,
                  target: int):
        """Once we received an Accept, send the requested data."""
        print("Received accept from {0}."
              .format(origin, dialogue_id, msg_id, target))

        # send the measurements to the client. for the sake of simplicity, they are hard-coded.
        self.send_message(dialogue_id, origin, b"temperature:15.0")
        self.send_message(dialogue_id, origin, b"humidity:0.7")
        self.send_message(dialogue_id, origin, b"air_pressure:1019.0")


if __name__ == '__main__':
    # create and connect the agent
    client_proxy = OEFNetworkProxy("weather_client", oef_addr="127.0.0.1", port=3333)
    station_proxy = OEFNetworkProxy("weather_station", oef_addr="127.0.0.1", port=3333)

    client = WeatherClient(client_proxy)
    station = WeatherStation(station_proxy)

    client.connect()
    station.connect()

    station.register_service(station.weather_service_description)

    query = Query([])

    client.search_services(0, query)

    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(
            client.async_run(),
            station.async_run()
        )
    )


