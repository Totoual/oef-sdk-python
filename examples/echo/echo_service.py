#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.

"""
Echo service agent
~~~~~~~~~~~~~~~~~

This script belongs to the ``echo`` example of OEF Agent development, and implements the echo service agent.
It assumes that an instance of the OEF Node is running at ``127.0.0.1:3333``.

The script does the following:

1. Instantiate a ``EchoServiceAgent``
2. Connect the agent to the OEF Node.
3. Register the agent as an ``echo`` service.
4. Run the agent, waiting for messages from the OEF.


The class ``EchoServiceAgent`` define the behaviour of the echo client agent.

* whenever he receives a message (see ``on_message`` method) from another agent,
he sends back the same message to the origin.

Other methods (e.g. ``on_cfp``, ``on_error`` etc.) are omitted, since not needed.

"""


from oef.agents import OEFAgent
from oef.schema import DataModel, Description

# Uncomment the following lines if you want more output
# import logging
# from oef.logger import set_logger
# set_logger("oef", logging.DEBUG)


class EchoServiceAgent(OEFAgent):
    """
    The class that defines the behaviour of the echo service agent.
    """

    def on_message(self, origin: str, dialogue_id: int, content: bytes):
        print("Received message: origin={}, dialogue_id={}, content={}".format(origin, dialogue_id, content))
        print("Sending {} back to {}".format(content, origin))
        self.send_message(dialogue_id, origin, content)


if __name__ == '__main__':

    # create agent and connect it to OEF
    server_agent = EchoServiceAgent("echo_server", oef_addr="127.0.0.1", oef_port=3333)
    server_agent.connect()

    # register a service on the OEF
    echo_model = DataModel("echo", [], "echo service.")
    echo_description = Description({}, echo_model)

    server_agent.register_service(echo_description)

    # run the agent
    server_agent.run()
