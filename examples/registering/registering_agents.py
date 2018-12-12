#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.

"""
A short script that show how an agent can register/unregister to the OEF.
"""
from oef.schema import Description

from oef.agents import OEFAgent

if __name__ == '__main__':
    agent = OEFAgent("agent_1", oef_addr="127.0.0.1", oef_port=3333)

    agent.connect()
    print("Agent successfully connected.")

    agent.register_agent(Description({}))
    print("Agent registered to the OEF Node.")

    agent.unregister_agent()
    print("Agent {} unregistered".format(agent.public_key))

