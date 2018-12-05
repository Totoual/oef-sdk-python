# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import asyncio
import logging
from typing import List, Tuple

import pytest
from oef.schema import Description

from oef import agent_pb2
from oef.messages import CFP_TYPES, PROPOSE_TYPES

from oef.query import Query

from oef.agents import LocalAgent
from oef.proxy import OEFLocalProxy


class Barrier:

    def __init__(self, target):
        self._lock = asyncio.Lock()
        self.target = target
        self.counter = 0
        self.barrier = asyncio.Semaphore(0)

    async def add(self):
        await self._lock.acquire()
        self.counter += 1
        if self.counter == self.target:
            self.barrier.release()
        self._lock.release()

    async def wait(self):
        await self.barrier.acquire()


class AgentTest(LocalAgent):
    """
    An agent used for tests.
    """

    def __init__(self, barrier: Barrier, *args, **kwargs):
        """
        Initialize an Local OEFAgent for tests.
        :param barrier: an object that implements a synchronization barrier.
        :param args: the positional arguments for the superclass.
        :param kwargs: the keyworded arguments for the superclass.
        """
        super().__init__(*args, **kwargs)
        self.barrier = barrier
        self.received_msg = []

    def _process_message(self, arguments: Tuple):
        self.received_msg.append(arguments)
        asyncio.ensure_future(self.barrier.add())

    def stop(self):
        if self._task:
            self._task.cancel()

    def on_message(self, origin: str, dialogue_id: int, content: bytes):
        self._process_message((origin, dialogue_id, content))

    def on_search_result(self, search_id: int, agents: List[str]):
        pass

    def on_cfp(self,
               origin: str,
               dialogue_id: int,
               msg_id: int,
               target: int,
               query: CFP_TYPES):
        self._process_message((origin, dialogue_id, msg_id, target, query))

    def on_propose(self,
                   origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int,
                   proposal: PROPOSE_TYPES):
        self._process_message((origin, dialogue_id, msg_id, target, proposal))

    def on_accept(self,
                  origin: str,
                  dialogue_id: int,
                  msg_id: int,
                  target: int):
        self._process_message((origin, dialogue_id, msg_id, target))

    def on_decline(self,
                   origin: str,
                   dialogue_id: int,
                   msg_id: int,
                   target: int):
        self._process_message((origin, dialogue_id, msg_id, target))

    def on_error(self,
                 operation: agent_pb2.Server.AgentMessage.Error.Operation,
                 dialogue_id: int,
                 message_id: int):
        pass


@pytest.fixture(scope="function")
def setup_agents(request):
    """
    Set up a local node and N agents.
    :param request: request.param is the number of agents to initialize.
    :return:
    """

    N = request.param[0]
    target = request.param[1]
    barrier = Barrier(target)

    local_node = OEFLocalProxy.LocalNode()
    agents = [AgentTest(barrier, "agent-{}".format(i), local_node) for i in range(N)]
    for a in agents:
        a.connect()

    # teardown for this fixture
    def teardown_agents():
        for a in agents:
            a.stop()

        for t in asyncio.Task.all_tasks():
            asyncio.get_event_loop().run_until_complete(t)

    request.addfinalizer(teardown_agents)

    return {"agents": agents, "barrier": barrier}


@pytest.mark.parametrize('setup_agents', [(3, 9)], indirect=True)
def test_on_message(setup_agents):
    """
    Test that 3 agents can send a simple message to themselves and each other and that
    the messages are properly processed and dispatched.
    """
    agent_0, agent_1, agent_2 = setup_agents["agents"]
    barrier = setup_agents["barrier"]

    msg = b"hello"

    agent_0.send_message(0, agent_0.public_key, msg)
    agent_0.send_message(0, agent_1.public_key, msg)
    agent_0.send_message(0, agent_2.public_key, msg)

    agent_1.send_message(0, agent_0.public_key, msg)
    agent_1.send_message(0, agent_1.public_key, msg)
    agent_1.send_message(0, agent_2.public_key, msg)

    agent_2.send_message(0, agent_0.public_key, msg)
    agent_2.send_message(0, agent_1.public_key, msg)
    agent_2.send_message(0, agent_2.public_key, msg)

    asyncio.ensure_future(asyncio.gather(
            agent_0.async_run(),
            agent_1.async_run(),
            agent_2.async_run()))
    asyncio.get_event_loop().run_until_complete(asyncio.wait_for(barrier.wait(), 1))

    assert len(agent_0.received_msg) == 3
    assert len(agent_1.received_msg) == 3
    assert len(agent_2.received_msg) == 3

    assert agent_0.received_msg[0] == (agent_0.public_key, 0, msg)
    assert agent_0.received_msg[1] == (agent_1.public_key, 0, msg)
    assert agent_0.received_msg[2] == (agent_2.public_key, 0, msg)
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, msg)
    assert agent_1.received_msg[1] == (agent_1.public_key, 0, msg)
    assert agent_1.received_msg[2] == (agent_2.public_key, 0, msg)
    assert agent_2.received_msg[0] == (agent_0.public_key, 0, msg)
    assert agent_2.received_msg[1] == (agent_1.public_key, 0, msg)
    assert agent_2.received_msg[2] == (agent_2.public_key, 0, msg)


@pytest.mark.parametrize('setup_agents', [(2, 3)], indirect=True)
def test_on_cfp(setup_agents):
    """
    Test that an agent can send a CFP to another agent, with different types of queries.
    """

    agent_0, agent_1 = setup_agents["agents"]
    barrier = setup_agents["barrier"]

    agent_0.send_cfp(0, agent_1.public_key, None, 1, 0)
    agent_0.send_cfp(0, agent_1.public_key, b"hello", 1, 0)
    agent_0.send_cfp(0, agent_1.public_key, Query([]), 1, 0)

    asyncio.ensure_future(agent_1.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.wait_for(barrier.wait(), 1))

    assert len(agent_1.received_msg) == 3
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0, None)
    assert agent_1.received_msg[1] == (agent_0.public_key, 0, 1, 0, b"hello")
    assert agent_1.received_msg[2] == (agent_0.public_key, 0, 1, 0, Query([]))


@pytest.mark.parametrize('setup_agents', [(2, 4)], indirect=True)
def test_on_propose(setup_agents):
    """
    Test that an agent can send a Propose to another agent, with different types of proposals.
    """

    agent_0, agent_1 = setup_agents["agents"]
    barrier = setup_agents["barrier"]

    agent_0.send_propose(0, agent_1.public_key, b"hello", 1, 0)
    agent_0.send_propose(0, agent_1.public_key, [], 1, 0)
    agent_0.send_propose(0, agent_1.public_key, [Description({})], 1, 0)
    agent_0.send_propose(0, agent_1.public_key, [Description({}), Description({})], 1, 0)

    asyncio.ensure_future(agent_1.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.wait_for(barrier.wait(), 1))

    assert len(agent_1.received_msg) == 4
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0, b"hello")
    assert agent_1.received_msg[1] == (agent_0.public_key, 0, 1, 0, [])
    assert agent_1.received_msg[2] == (agent_0.public_key, 0, 1, 0, [Description({})])
    assert agent_1.received_msg[3] == (agent_0.public_key, 0, 1, 0, [Description({}), Description({})])


@pytest.mark.parametrize('setup_agents', [(2, 1)], indirect=True)
def test_on_propose(setup_agents):
    """
    Test that an agent can send a Propose to another agent, with different types of proposals.
    """

    agent_0, agent_1 = setup_agents["agents"]
    barrier = setup_agents["barrier"]

    agent_0.send_accept(0, agent_1.public_key, 1, 0)

    asyncio.ensure_future(agent_1.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.wait_for(barrier.wait(), 1))

    assert len(agent_1.received_msg) == 1
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0)


@pytest.mark.parametrize('setup_agents', [(2, 1)], indirect=True)
def test_on_decline(setup_agents):
    """
    Test that an agent can send a Propose to another agent, with different types of proposals.
    """

    agent_0, agent_1 = setup_agents["agents"]
    barrier = setup_agents["barrier"]

    agent_0.send_decline(0, agent_1.public_key, 1, 0)
    asyncio.ensure_future(agent_1.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.wait_for(barrier.wait(), 1))

    assert len(agent_1.received_msg) == 1
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0)
