import sys
import os

from oef.proxy import OEFNetworkProxy

PACKAGE_PARENT = '../oef'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import asyncio


if __name__ == "__main__":
    connection = OEFNetworkProxy("PythonAgent", "127.0.0.1")
    
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(connection.connect())
