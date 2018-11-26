# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


from oef.agents import OEFAgent
from oef.api import DataModel, Description

import logging
from oef.logger import set_logger
set_logger("oef", logging.DEBUG)


class EchoServerAgent(OEFAgent):

    def on_message(self, origin: str, conversation_id: str, content: bytes):
        print("Received message: origin={}, conversation_id={}, content={}".format(origin, conversation_id, content))
        self.send_message(conversation_id, origin, b"ciao")


if __name__ == '__main__':

    # create agent and connect it to OEF
    agent = EchoServerAgent("echo_server", oef_addr="127.0.0.1", oef_port=3333)
    agent.connect()

    # register a data service on the OEF
    echo_model = DataModel("echo", [], "echo data service.")
    echo_description = Description({}, echo_model)

    agent.register_service(echo_description)

    # run the agent
    agent.run()
