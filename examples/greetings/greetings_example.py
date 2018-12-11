# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
"""
A simple example with OEF Agents that greet each other.

You can run this script in two mode:

- network: the agents interact via an OEF Node (check that it's running before launching the script)
- local: the agents interacts via a local implementation of the OEF Node.

"""

import asyncio
from argparse import ArgumentParser

from typing import List

from oef.agents import Agent
from oef.proxy import OEFLocalProxy, OEFNetworkProxy
from oef.schema import DataModel, Description
from oef.query import Query


parser = ArgumentParser("greetings-example", "A simple example with OEF Agents that greet each other.")
parser.add_argument("--local", type=bool, help="Run the example with a local implementation of the OEF Node.")


class GreetingsAgent(Agent):

    def on_message(self, origin: str, dialogue_id: int, content: bytes):
        print("[{}]: Received message: origin={}, dialogue_id={}, content={}"
              .format(self.public_key, origin, dialogue_id, content))
        if content == b"hello":
            print("[{}]: Sending greetings message to {}".format(self.public_key, origin))
            self.send_message(dialogue_id, origin, b"greetings")

    def on_search_result(self, search_id: int, agents: List[str]):
        if len(agents) > 0:
            print("[{}]: Agents found: {}".format(self.public_key, agents))
            for a in agents:
                self.send_message(0, a, b"hello")
        else:
            print("[{}]: No agent found.".format(self.public_key))


if __name__ == '__main__':

    args = parser.parse_args()
    if args.local:
        local_node = OEFLocalProxy.LocalNode()
        client_proxy = OEFLocalProxy("greetings_client", local_node)
        server_proxy = OEFLocalProxy("greetings_server", local_node)
    else:
        client_proxy = OEFNetworkProxy("greetings_client", oef_addr="127.0.0.1", port=3333)
        server_proxy = OEFNetworkProxy("greetings_server", oef_addr="127.0.0.1", port=3333)

    # create agents
    client_agent = GreetingsAgent(client_proxy)
    server_agent = GreetingsAgent(server_proxy)

    # connect the agents to the OEF
    client_agent.connect()
    server_agent.connect()

    # register the greetings service agent on the OEF
    greetings_model = DataModel("greetings", [], "Greetings service.")
    greetings_description = Description({}, greetings_model)
    server_agent.register_service(greetings_description)

    # the client executes the search for greetings services
    query = Query([], greetings_model)

    print("[{}]: Search for 'greetings' services.".format(client_agent.public_key))
    client_agent.search_services(0, query)

    # run both agents concurrently
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        client_agent.async_run(),
        server_agent.async_run(),
      )
    )
