#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.

import asyncio

from oef.proxy import OEFNetworkProxy

if __name__ == "__main__":
    connections = []
    for i in range(10):
        connections.append(OEFNetworkProxy("PythonAgent" + str(i), "127.0.0.1"))
    event_loop = asyncio.get_event_loop()
    for conn in connections:
        event_loop.run_until_complete(conn.connect())
