# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
from typing import List

from oef.agents import OEFAgent
from oef.api import DataModel, Query

import logging
from oef.logger import set_logger
set_logger("oef", logging.DEBUG)


class EchoClientAgent(OEFAgent):

    def on_message(self, origin: str, conversation_id: str, content: bytes):
        print("Received message: origin={}, conversation_id={}, content={}".format(origin, conversation_id, content))

    def on_search_result(self, agents: List[str]):
        print("Agent found: ", agents)
        self.send_message("uuid", agents[0], b"hello")


if __name__ == '__main__':

    # define an OEF Agent
    agent = EchoClientAgent("echo_client", oef_addr="127.0.0.1", oef_port=3333)

    # connect it to the OEF Node
    agent.connect()

    # query OEF for DataService providers
    echo_model = DataModel("echo", [], "Echo data service.")
    echo_query = Query([], echo_model)
    agent.search_services(echo_query)

    # wait for events
    agent.run()
