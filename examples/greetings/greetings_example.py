# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import asyncio
import uuid
from typing import List

from oef.agents import OEFAgent
from oef.schema import DataModel, Description
from oef.query import Query


class GreetingsAgent(OEFAgent):

    def on_message(self, origin: str, conversation_id: str, content: bytes):
        print("{}: Received message: origin={}, conversation_id={}, content={}"
              .format(self._pubkey, origin, conversation_id, content))
        if content == b"hello":
            print("{}: Sending greetings message to {}".format(self._pubkey, origin))
            self.send_message(conversation_id, origin, b"greetings")

    def on_search_result(self, agents: List[str]):
        if len(agents) > 0:
            print("{}, Agents found: {}".format(self._pubkey, agents))
            for a in agents:
                self.send_message(str(uuid.uuid4()), a, b"hello")
        else:
            print("No agent found.")


if __name__ == '__main__':

    # create agents
    client_agent = GreetingsAgent("greetings_client", oef_addr="127.0.0.1", oef_port=3333)
    server_agent = GreetingsAgent("greetings_server", oef_addr="127.0.0.1", oef_port=3333)

    # connect the agents to the OEF
    client_agent.connect()
    server_agent.connect()

    # register the greetings service agent on the OEF
    greetings_model = DataModel("greetings", [], "Greetings service.")
    greetings_description = Description({}, greetings_model)
    server_agent.register_service(greetings_description)

    # the client executes the search for greetings services
    query = Query([], greetings_model)
    client_agent.search_services(query)

    # run both agents concurrently
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        client_agent.async_run(),
        server_agent.async_run(),
      )
    )
