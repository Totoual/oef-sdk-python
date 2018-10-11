import sys
import os

PACKAGE_PARENT = '../oef_python'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import asyncio

from api import Description, AttributeSchema, AttributeInconsistencyException,\
    generate_schema, OEFProxy

if __name__ == "__main__":
    connection = OEFProxy("PythonAgent", "127.0.0.1")
    
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(connection.connect())
