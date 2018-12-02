# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


from oef.agents import OEFAgent
from oef.schema import DataModel, Description

import logging
from oef.logger import set_logger
set_logger("oef", logging.DEBUG)


class EchoServiceAgent(OEFAgent):

    def on_message(self, origin: str, dialogue_id: int, content: bytes):
        print("Received message: origin={}, dialogue_id={}, content={}".format(origin, dialogue_id, content))
        print("Sending {} back to {}".format(content, origin))
        self.send_message(dialogue_id, origin, content)


if __name__ == '__main__':

    # create agent and connect it to OEF
    server_agent = EchoServiceAgent("echo_server", oef_addr="127.0.0.1", oef_port=3333)
    server_agent.connect()

    # register a data service on the OEF
    echo_model = DataModel("echo", [], "echo data service.")
    echo_description = Description({}, echo_model)

    server_agent.register_service(echo_description)

    # run the agent
    server_agent.run()
