import asyncio
import os
import sys
from typing import List

PACKAGE_PARENT = '../../oef_python'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from client_agent import LocalizableAgent


if __name__ == '__main__':
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
