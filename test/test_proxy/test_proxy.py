# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import asyncio
from typing import List

import pytest

from oef.schema import Description, DataModel

from oef.query import Query

from oef.proxy import OEFLocalProxy, OEFNetworkProxy
from test.test_proxy.agent_test import AgentTest

_ASYNCIO_DELAY = 0.1


def _init_n_agents(n, local: bool) -> List[AgentTest]:
    if local:
        local_node = OEFLocalProxy.LocalNode()
        proxies = [OEFLocalProxy("agent-{}".format(i), local_node) for i in range(n)]
    else:
        proxies = [OEFNetworkProxy("agent-{}".format(i), "127.0.0.1", 3333) for i in range(n)]

    agents = [AgentTest(proxy) for proxy in proxies]
    for a in agents:
        a.connect()

    return agents


def _stop_agents(agents):
    for a in agents:
        a.stop()

    for t in asyncio.Task.all_tasks():
        asyncio.get_event_loop().run_until_complete(t)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_message(oef_network_node, is_local):
    """
    Test that 3 agents can send a simple message to themselves and each other and that
    the messages are properly processed and dispatched.
    """

    agents = _init_n_agents(3, is_local)
    agent_0, agent_1, agent_2 = agents

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
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

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

    _stop_agents(agents)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_cfp(oef_network_node, is_local):
    """
    Test that an agent can send a CFP to another agent, with different types of queries.
    """

    agents = _init_n_agents(2, is_local)
    agent_0, agent_1 = agents

    agent_0.send_cfp(0, agent_1.public_key, None, 1, 0)
    agent_0.send_cfp(0, agent_1.public_key, b"hello", 1, 0)
    agent_0.send_cfp(0, agent_1.public_key, Query([]), 1, 0)

    asyncio.ensure_future(agent_1.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

    assert len(agent_1.received_msg) == 3
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0, None)
    assert agent_1.received_msg[1] == (agent_0.public_key, 0, 1, 0, b"hello")
    assert agent_1.received_msg[2] == (agent_0.public_key, 0, 1, 0, Query([]))

    _stop_agents(agents)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_propose(oef_network_node, is_local):
    """
    Test that an agent can send a Propose to another agent, with different types of proposals.
    """

    agents = _init_n_agents(2, is_local)
    agent_0, agent_1 = agents

    agent_0.send_propose(0, agent_1.public_key, b"hello", 1, 0)
    agent_0.send_propose(0, agent_1.public_key, [], 1, 0)
    agent_0.send_propose(0, agent_1.public_key, [Description({})], 1, 0)
    agent_0.send_propose(0, agent_1.public_key, [Description({}), Description({})], 1, 0)

    asyncio.ensure_future(agent_1.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

    assert len(agent_1.received_msg) == 4
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0, b"hello")
    assert agent_1.received_msg[1] == (agent_0.public_key, 0, 1, 0, [])
    assert agent_1.received_msg[2] == (agent_0.public_key, 0, 1, 0, [Description({})])
    assert agent_1.received_msg[3] == (agent_0.public_key, 0, 1, 0, [Description({}), Description({})])

    _stop_agents(agents)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_accept(oef_network_node, is_local):
    """
    Test that an agent can send an Accept to another agent, with different types of proposals.
    """

    agents = _init_n_agents(2, is_local)
    agent_0, agent_1 = agents

    agent_0.send_accept(0, agent_1.public_key, 1, 0)

    asyncio.ensure_future(agent_1.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

    assert len(agent_1.received_msg) == 1
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0)

    _stop_agents(agents)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_decline(oef_network_node, is_local):
    """
    Test that an agent can send a Decline to another agent, with different types of proposals.
    """

    agents = _init_n_agents(2, is_local)
    agent_0, agent_1 = agents

    agent_0.send_decline(0, agent_1.public_key, 1, 0)
    asyncio.ensure_future(agent_1.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

    assert len(agent_1.received_msg) == 1
    assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0)

    _stop_agents(agents)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_search_result_services(oef_network_node, is_local):
    """
    Test that an agent can do a search for services.
    """

    agents = _init_n_agents(3, is_local)
    agent_0, agent_1, agent_2 = agents

    dummy_datamodel = DataModel("dummy_datamodel", [])
    agent_1.register_service(Description({}, dummy_datamodel))
    agent_2.register_service(Description({}, dummy_datamodel))

    agent_0.search_services(0, Query([], dummy_datamodel))
    asyncio.ensure_future(agent_0.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

    assert len(agent_0.received_msg) == 1
    assert agent_0.received_msg[0] == (0, ["agent-1", "agent-2"])

    _stop_agents(agents)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_search_result_agents(oef_network_node, is_local):
    """
    Test that an agent can do a search for agents.
    """

    agents = _init_n_agents(3, is_local)
    agent_0, agent_1, agent_2 = agents

    dummy_datamodel = DataModel("dummy_datamodel", [])
    agent_1.register_agent(Description({}, dummy_datamodel))
    agent_2.register_agent(Description({}, dummy_datamodel))

    agent_0.search_agents(0, Query([], dummy_datamodel))
    asyncio.ensure_future(agent_0.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

    assert len(agent_0.received_msg) == 1
    assert agent_0.received_msg[0] == (0, ["agent-1", "agent-2"])

    _stop_agents(agents)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_unregister_agent(oef_network_node, is_local):
    """
    Test that the unregistration of agents works correctly.
    """

    agents = _init_n_agents(2, is_local)
    agent_0, agent_1 = agents

    dummy_datamodel = DataModel("dummy_datamodel", [])
    agent_1.register_agent(Description({}, dummy_datamodel))
    agent_1.unregister_agent()

    agent_0.search_agents(0, Query([], dummy_datamodel))
    asyncio.ensure_future(agent_0.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

    assert len(agent_0.received_msg) == 1
    assert agent_0.received_msg[0] == (0, [])

    _stop_agents(agents)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_unregister_service(oef_network_node, is_local):
    """
    Test that the unregistration of agents works correctly.
    """

    agents = _init_n_agents(2, is_local)
    agent_0, agent_1 = agents

    dummy_datamodel = DataModel("dummy_datamodel", [])
    dummy_service_description = Description({}, dummy_datamodel)
    agent_1.register_service(dummy_service_description)
    agent_1.unregister_service(dummy_service_description)

    agent_0.search_services(0, Query([], dummy_datamodel))
    asyncio.ensure_future(agent_0.async_run())
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

    assert len(agent_0.received_msg) == 1
    assert agent_0.received_msg[0] == (0, [])

    _stop_agents(agents)
