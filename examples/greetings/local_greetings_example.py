# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


import asyncio
import logging

from typing import List

from oef.agents import OEFAgent, LocalAgent
from oef.logger import set_logger
from oef.proxy import OEFLocalProxy
from oef.schema import DataModel, Description
from oef.query import Query


class GreetingsAgent(LocalAgent):

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
    set_logger("oef", level=logging.DEBUG)

    local_node = OEFLocalProxy.LocalNode()

    # create agents
    client_agent = GreetingsAgent("greetings_client", local_node)
    server_agent = GreetingsAgent("greetings_server", local_node)

    # connect the agents to the OEF
    client_agent.connect()
    server_agent.connect()

    # register the greetings service agent on the OEF
    greetings_model = DataModel("greetings", [], "Greetings service.")
    greetings_description = Description({}, greetings_model)
    server_agent.register_service(greetings_description)

    # the client executes the search for greetings services
    query = Query([], greetings_model)
    client_agent.search_services(0, query)

    # run both agents concurrently
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        client_agent.async_run(),
        server_agent.async_run(),
        local_node.run()
      )
    )
