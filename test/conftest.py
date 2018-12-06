# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import inspect
import os
import subprocess
import time

import pytest

ROOT_DIR = ".."
OUR_DIRECTORY = os.path.dirname(inspect.getfile(inspect.currentframe()))
FULL_PATH = [OUR_DIRECTORY, ROOT_DIR, "OEFCore", "build", "apps", "node", "Node"]
PATH_TO_NODE_EXEC = os.path.join(*FULL_PATH)


@pytest.fixture(scope="function")
def oef_network_node(request):
    FNULL = open(os.devnull, 'w')
    p = subprocess.Popen(PATH_TO_NODE_EXEC, stdout=FNULL, stderr=subprocess.STDOUT)
    time.sleep(0.001)

    def teardown():
        p.kill()

    request.addfinalizer(teardown)
