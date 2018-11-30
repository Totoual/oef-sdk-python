# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

"""
Test that our API works
"""

import contextlib
import inspect
import os

import subprocess

NODE_FROM_ROOT_PATH = "./Node"
PATH_TO_ROOT = ".."
OUR_DIRECTORY = os.path.dirname(inspect.getfile(inspect.currentframe()))
PATH_TO_NODE_EXEC = os.path.join(OUR_DIRECTORY, PATH_TO_ROOT, NODE_FROM_ROOT_PATH)

@contextlib.contextmanager
def oef_server_context():
    """
    Contextlib that alllows us to start up an instance of the OEF server for use in testing.

    Used::
        with oef_server_context():
            # do some stuff that uses the OEF server
    After exiting the with block the sever will be torn down
    """
    # assume that we can find the Node binary relative to this file
    print("PATH_TO_NODE_EXEC: ", PATH_TO_NODE_EXEC)
    node_process = subprocess.Popen(PATH_TO_NODE_EXEC)
    try:
        yield
    finally:
        node_process.kill()
        node_process = None

# TODO: test connection that do not require 'Node' executable (from OEFCore build)
# def test_can_connect_to_oef():
#     """
#     Simple test that sees if we can connect to the OEF on localhost without errors
#     """
#     with oef_server_context():
#         connection = OEFProxy("pub_key", "127.0.0.1")
#
#     # if we get here without errors we have passed
