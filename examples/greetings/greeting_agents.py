#!/usr/bin/env python3
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


"""
A simple example with OEF Agents that greet each other.
The agents interact via an OEF Node on the network.
"""

import asyncio
from argparse import ArgumentParser
from typing import List
from oef.agents import Agent
from oef.proxy import OEFNetworkProxy
from oef.query import Query, Constraint, Eq
from oef.schema import DataModel, Description, AttributeSchema

parser = ArgumentParser("greetings-agents", "A simple example with OEF Agents that greet each other.")
parser.add_argument("--addr", default="127.0.0.1", help="IP address of the OEF Node.")
parser.add_argument("--port", default=3333, help="Port for the connection with the OEF Node.")


class GreetingsAgent(Agent):
    """A class that implements the greeting agent."""

    def on_message(self, msg_id: int, dialogue_id: int, origin: str, content: bytes):
        print("[{}]: Received message: msg_id={}, dialogue_id={}, origin={}, content={}"
              .format(self.public_key, msg_id, dialogue_id, origin, content))
        if content == b"hello":
            print("[{}]: Sending greetings message to {}".format(self.public_key, origin))
            self.send_message(1, dialogue_id, origin, b"greetings")
            self.stop()
        if content == b"greetings":
            self.stop()

    def on_search_result(self, search_id: int, agents: List[str]):
        if len(agents) > 0:
            print("[{}]: Agents found: {}".format(self.public_key, agents))
            for a in agents:
                self.send_message(0, 0, a, b"hello")
        else:
            print("[{}]: No agent found.".format(self.public_key))
            self.stop()


if __name__ == '__main__':

    args = parser.parse_args()

    client_proxy = OEFNetworkProxy("greetings_client", oef_addr=args.addr, port=args.port)
    server_proxy = OEFNetworkProxy("greetings_server", oef_addr=args.addr, port=args.port)

    # create agents
    client_agent = GreetingsAgent(client_proxy)
    server_agent = GreetingsAgent(server_proxy)

    # connect the agents to the OEF
    client_agent.connect()
    server_agent.connect()

    # register the greetings service agent on the OEF
    say_hello = AttributeSchema("say_hello", bool, True, "The agent answers to 'hello' messages.")
    greetings_model = DataModel("greetings", [say_hello], "Greetings service.")
    greetings_description = Description({"say_hello": True}, greetings_model)
    server_agent.register_service(0, greetings_description)

    # the client executes the search for greetings services
    # we are looking for services that answers to "hello" messages
    query = Query([Constraint("say_hello", Eq(True))], greetings_model)

    print("[{}]: Search for 'greetings' services. search_id={}".format(client_agent.public_key, 0))
    client_agent.search_services(0, query)

    # run the agents
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            client_agent.async_run(),
            server_agent.async_run()))
    finally:
        client_agent.stop()
        server_agent.stop()

        client_agent.disconnect()
        server_agent.disconnect()
