# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import List

from oef.agents import OEFAgent
from oef.schema import DataModel
from oef.query import Query

import logging
from oef.logger import set_logger
set_logger("oef", logging.DEBUG)


class EchoClientAgent(OEFAgent):

    def on_message(self, origin: str, dialogue_id: int, content: bytes):
        print("Received message: origin={}, dialogue_id={}, content={}".format(origin, dialogue_id, content))

    def on_search_result(self, search_id: int, agents: List[str]):
        if len(agents) > 0:
            print("Agents found: ", agents)
            msg = b"hello"
            for agent in agents:
                print("Sending {} to {}".format(msg, agent))
                self.send_message(0, agent, msg)
        else:
            print("No agent found.")


if __name__ == '__main__':

    # define an OEF Agent
    client_agent = EchoClientAgent("echo_client", oef_addr="127.0.0.1", oef_port=3333)

    # connect it to the OEF Node
    client_agent.connect()

    # query OEF for DataService providers
    echo_model = DataModel("echo", [], "Echo data service.")
    echo_query = Query([], echo_model)

    print("Make search to the OEF")
    client_agent.search_services(0, echo_query)

    # wait for events
    client_agent.run()
