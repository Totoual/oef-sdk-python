# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Marco Favorito <marco.favorito@fetch.ai>
import asyncio
import os
import sys
from typing import List

PACKAGE_PARENT = '../../oef_python'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from .client_agent import LocalizableAgent

import argparse
parser = argparse.ArgumentParser(description='Run the demo.')

def _n_type(n):
    """
    Check if the n provided to the script is valid for our purposes
    :param n:
    :return: The value
    """
    try:
        result = int(n)
        assert 1 < result < 10000
    except Exception:
        raise argparse.ArgumentTypeError("the number of agents is not valid.")

    return result


parser.add_argument("N", type=_n_type, help="The number of agents [1, 10000]")

def main():
    # remember to run the OEFCore ./Node in another terminal

    # number of agent to be instantiated
    N = 10

    # instantiate and register every agent
    agents: List[LocalizableAgent] = [LocalizableAgent("agent_{:04d}".format(n)) for n in range(N)]

    for a in agents:
        a.register()
        print("Agent %s created" % a.name)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            *(a.search_other_agent_nearby() for a in agents)
        )
    )
    loop.close()


if __name__ == '__main__':
    main()