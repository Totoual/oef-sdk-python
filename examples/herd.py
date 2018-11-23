import sys
import os

from oef.api import OEFProxy

PACKAGE_PARENT = '../oef'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import asyncio

if __name__ == "__main__":
    connections = []
    for i in range(10):
        connections.append(OEFProxy("PythonAgent" + str(i), "127.0.0.1"))
    event_loop = asyncio.get_event_loop()
    for conn in connections:
        event_loop.run_until_complete(conn.connect())
