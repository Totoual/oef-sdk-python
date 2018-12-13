#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#   Copyright 2018 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------


import asyncio

from oef.proxy import OEFNetworkProxy

if __name__ == "__main__":
    connections = []
    for i in range(10):
        connections.append(OEFNetworkProxy("PythonAgent" + str(i), "127.0.0.1"))
    event_loop = asyncio.get_event_loop()
    for conn in connections:
        event_loop.run_until_complete(conn.connect())
