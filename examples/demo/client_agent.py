# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Marco Favorito <marco.favorito@fetch.ai>
import asyncio
import os
import random
import sys
from typing import List

PACKAGE_PARENT = '../oef_python'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from oef_python.api import AttributeSchema, OEFProxy, DataModel, Eq, Query, Constraint, PROPOSE_TYPES, Description, \
    Range

ATTRIBUTE_LOCATION_X = AttributeSchema("location_x", float, True, "x coordinate of the agent")
ATTRIBUTE_LOCATION_Y = AttributeSchema("location_y", float, True, "y coordinate of the agent")

AGENT_DATA_MODEL = DataModel("location_data",
                             [ATTRIBUTE_LOCATION_X, ATTRIBUTE_LOCATION_Y],
                             "A localizable agent")

class LocalizableAgent(object):

    def __init__(self, name: str, host_path: str="127.0.0.1"):
        self.name = name
        self.host_path = host_path
        self._connection: OEFProxy = self._get_connection()
        self.x, self.y = random.random(), random.random()
        self.description = Description({"location_x": self.x, "location_y": self.y}, AGENT_DATA_MODEL)

    def _get_connection(self) -> OEFProxy:
        connection = OEFProxy(self.name, self.host_path)
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(connection.connect())
        return connection

    def onSearchResult(self, agents: List[str]) -> None:
        print("{0}: #agents:{1}, Agent.onSearchResult {2}".format(self.name, len(agents), agents))

    def register(self):
        self._connection.register_agent(self.description)

    async def search_other_agent_nearby(self):
        query = Query([Constraint(ATTRIBUTE_LOCATION_X, Range((self.x - 0.25, self.x + 0.25))),
                       Constraint(ATTRIBUTE_LOCATION_Y, Range((self.y - 0.25, self.y + 0.25)))],
                      AGENT_DATA_MODEL)

        self._connection.search_agents(query)
        await self._connection.loop(self)
