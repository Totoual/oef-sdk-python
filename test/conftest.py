# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import subprocess
import time

import pytest


@pytest.fixture(scope="function")
def oef_network_node(request):
    p = subprocess.Popen("OEFCore/build/apps/node/Node")
    time.sleep(0.1)

    def teardown():
        p.kill()

    request.addfinalizer(teardown)
