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
from typing import List, Optional, Callable

from oef.proxy import OEFNetworkProxy, OEFProxy

from oef.dialogue import SingleDialogue, DialogueAgent, GroupDialogues
from oef.query import Query, Constraint, Eq

from weather_schema import WEATHER_DATA_MODEL
from oef.schema import Description


from oef.messages import PROPOSE_TYPES, CFP_TYPES, OEFErrorOperation
from oef.agents import Agent

import random


class WeatherClient(DialogueAgent):
    """Class that implements the behavior of the weather client."""

    def __init__(self, oef_proxy: OEFProxy):
        super().__init__(oef_proxy)
        self.group = None

    def on_search_result(self, search_id: int, agents: List[str]):
        """For every agent returned in the service search, send a CFP to obtain resources from them."""
        print("Agent found: {0}".format(agents))
        self.group = WeatherGroupDialogues(self, agents)

    def on_new_cfp(self, from_: str, dialogue_id: int, msg_id: int, target: int, query: CFP_TYPES) -> None:
        pass

    def on_new_message(self, from_: str, dialogue_id: int, content: str) -> None:
        pass

    def on_connection_error(self, operation: OEFErrorOperation) -> None:
        pass


class WeatherClientDialogue(SingleDialogue):

    def __init__(self, agent: DialogueAgent,
                 destination: str,
                 notify: Callable,
                 id_: Optional[int] = None):
        super().__init__(agent, destination, id_)
        self.notify = notify  # type: Callable
        self.data_received = 0
        self.agent.send_cfp(self.id, destination, None)

    def on_error(self):
        pass

    def on_propose(self, origin: str, dialogue_id: int, msg_id: int, target: int, proposals: PROPOSE_TYPES):
        print("Received propose from agent {0}".format(origin))
        assert type(proposals) == list and len(proposals) == 1
        proposal = proposals[0]
        print("Proposal: {}".format(proposal.values))
        self.notify(self.destination, proposal.values["price"])

    def on_message(self, origin: str,
                   dialogue_id: int,
                   content: bytes):
        """Extract and print data from incoming (simple) messages."""
        key, value = content.decode().split(":")
        print("Received measurement from {}: {}={}".format(origin, key, float(value)))
        self.data_received += 1
        if self.data_received == 3:
            self.agent.stop()

    def on_cfp(self, origin: str, dialogue_id: int, msg_id: int, target: int, query: CFP_TYPES) -> None:
        pass

    def on_accept(self, origin: str, dialogue_id: int, msg_id: int, target: int) -> None:
        pass

    def on_decline(self, origin: str, dialogue_id: int, msg_id: int, target: int) -> None:
        pass

    def send_answer(self, winner: str):
        if self.destination == winner:
            print("Sending accept to {}".format(self.destination))
            self.agent.send_accept(self.id, self.destination, 2, 1)
        else:
            print("Sending decline to {}".format(self.destination))
            self.agent.send_decline(self.id, self.destination, 2, 1)


class WeatherGroupDialogues(GroupDialogues):
    
    def __init__(self, agent: DialogueAgent, agents: List[str]):
        super().__init__(agent)
        dialogues = [WeatherClientDialogue(agent, a,
                                           lambda from_, price: self.update(from_, price))
                     for a in agents]
        self.add_agents(dialogues)
    
    def better(self, price1:int, price2: int) -> bool:
        return price1 < price2

    def finished(self):
        print("Best price: {} from station {}".format(self.best_price, self.best_agent))
        for _, d in self.dialogues.items():
            d.send_answer(self.best_agent)


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

    def __init__(self, oef_proxy: OEFProxy):
        super().__init__(oef_proxy)
        self.price = random.random()

    def on_cfp(self, origin: str,
               dialogue_id: int,
               msg_id: int,
               target: int,
               query: CFP_TYPES):
        """Send a simple Propose to the sender of the CFP."""
        print("{}: Received CFP from {}".format(self.public_key, origin))

        # prepare the proposal with a given price.
        proposal = Description({"price": self.price})
        self.send_propose(dialogue_id, origin, [proposal], msg_id + 1, target + 1)

    def on_accept(self, origin: str,
                  dialogue_id: int,
                  msg_id: int,
                  target: int):
        """Once we received an Accept, send the requested data."""
        print("Received accept from {0}."
              .format(origin, dialogue_id, msg_id, target))

        # send the measurements to the client. for the sake of simplicity, they are hard-coded.
        self.send_message(0, dialogue_id, origin, b"temperature:15.0")
        self.send_message(0, dialogue_id, origin, b"humidity:0.7")
        self.send_message(0, dialogue_id, origin, b"air_pressure:1019.0")

        self.stop()

    def on_decline(self, origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int, ):
        self.stop()


if __name__ == '__main__':
    # create and connect the agent
    client_proxy = OEFNetworkProxy("weather_client", oef_addr="127.0.0.1", port=3333)
    client = WeatherClient(client_proxy)
    client.connect()

    N = 20
    station_proxies = [OEFNetworkProxy("weather_station_{:02d}".format(i),
                                       oef_addr="127.0.0.1", port=3333) for i in range(N)]

    stations = [WeatherStation(station_proxy) for station_proxy in station_proxies]
    for station in stations:
        station.connect()
        station.register_service(0, station.weather_service_description)

    query = Query([
        Constraint("temperature", Eq(True)),
        Constraint("air_pressure", Eq(True)),
        Constraint("humidity", Eq(True))],
        WEATHER_DATA_MODEL)

    client.search_services(0, query)

    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(
            client.async_run(),
            *[station.async_run() for station in stations]
        )
    )


