# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#   Copyright 2018 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

import asyncio
import contextlib
from typing import List

import pytest

from oef.schema import Description, DataModel

from oef.query import Query

from oef.proxy import OEFLocalProxy, OEFNetworkProxy
from test.test_proxy.agent_test import AgentTest


_ASYNCIO_DELAY = 0.1


@contextlib.contextmanager
def setup_test_agents(n: int, local: bool, prefix: str="") -> List[AgentTest]:
    agents, task = _init_context(n, local, prefix)
    try:
        yield agents
    except Exception:
        raise
    finally:
        if task:
            task.cancel()
        _stop_agents(agents)


def _init_context(n: int, local: bool, prefix: str= ""):
    public_key_prefix = prefix + "-" if prefix else ""
    _task = None
    if local:
        local_node = OEFLocalProxy.LocalNode()
        proxies = [OEFLocalProxy("{}agent-{}".format(public_key_prefix, i), local_node) for i in range(n)]
        _task = asyncio.ensure_future(local_node.run())
    else:
        proxies = [OEFNetworkProxy("{}agent-{}".format(public_key_prefix, i), "127.0.0.1", 3333) for i in range(n)]

    agents = [AgentTest(proxy) for proxy in proxies]
    for a in agents:
        a.connect()

    return agents, _task


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
    with setup_test_agents(3, is_local, prefix="on_message") as agents:
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


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_cfp(oef_network_node, is_local):
    """
    Test that an agent can send a CFP to another agent, with different types of queries.
    """

    with setup_test_agents(2, is_local, prefix="on_cfp") as agents:
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


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_propose(oef_network_node, is_local):
    """
    Test that an agent can send a Propose to another agent, with different types of proposals.
    """

    with setup_test_agents(2, is_local, prefix="on_propose") as agents:

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


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_accept(oef_network_node, is_local):
    """
    Test that an agent can send an Accept to another agent, with different types of proposals.
    """

    with setup_test_agents(2, is_local, prefix="on_accept") as agents:
        agent_0, agent_1 = agents

        agent_0.send_accept(0, agent_1.public_key, 1, 0)

        asyncio.ensure_future(agent_1.async_run())
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        assert len(agent_1.received_msg) == 1
        assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_decline(oef_network_node, is_local):
    """
    Test that an agent can send a Decline to another agent, with different types of proposals.
    """

    with setup_test_agents(2, is_local, prefix="on_decline") as agents:
        agent_0, agent_1 = agents

        agent_0.send_decline(0, agent_1.public_key, 1, 0)
        asyncio.ensure_future(agent_1.async_run())
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        assert len(agent_1.received_msg) == 1
        assert agent_1.received_msg[0] == (agent_0.public_key, 0, 1, 0)


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_search_result_services(oef_network_node, is_local):
    """
    Test that an agent can do a search for services.
    """

    with setup_test_agents(3, is_local, prefix="search_services") as agents:

        agent_0, agent_1, agent_2 = agents

        dummy_datamodel = DataModel("dummy_datamodel", [])
        agent_1.register_service(Description({}, dummy_datamodel))
        agent_2.register_service(Description({}, dummy_datamodel))

        agent_0.search_services(0, Query([], dummy_datamodel))
        asyncio.ensure_future(agent_0.async_run())
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))
        agent_1.unregister_service(Description({}, dummy_datamodel))
        agent_2.unregister_service(Description({}, dummy_datamodel))

        assert len(agent_0.received_msg) == 1
        assert agent_0.received_msg[0] == (0, [agent_1.public_key, agent_2.public_key])


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_on_search_result_agents(oef_network_node, is_local):
    """
    Test that an agent can do a search for agents.
    """

    with setup_test_agents(3, is_local, prefix="search_agents") as agents:

        agent_0, agent_1, agent_2 = agents

        dummy_datamodel = DataModel("dummy_datamodel", [])
        agent_1.register_agent(Description({}, dummy_datamodel))
        agent_2.register_agent(Description({}, dummy_datamodel))

        agent_0.search_agents(0, Query([], dummy_datamodel))
        asyncio.ensure_future(agent_0.async_run())
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))
        agent_1.unregister_agent()
        agent_2.unregister_agent()

        assert len(agent_0.received_msg) == 1
        assert agent_0.received_msg[0] == (0, [agent_1.public_key, agent_2.public_key])


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_unregister_agent(oef_network_node, is_local):
    """
    Test that the unregistration of agents works correctly.
    """

    with setup_test_agents(2, is_local, prefix="unregister_agent") as agents:

        agent_0, agent_1 = agents

        dummy_datamodel = DataModel("dummy_datamodel", [])
        agent_1.register_agent(Description({}, dummy_datamodel))
        agent_1.unregister_agent()

        agent_0.search_agents(0, Query([], dummy_datamodel))
        asyncio.ensure_future(agent_0.async_run())
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        assert len(agent_0.received_msg) == 1
        assert agent_0.received_msg[0] == (0, [])


@pytest.mark.parametrize("is_local", [True, False], ids=["local", "networked"])
def test_unregister_service(oef_network_node, is_local):
    """
    Test that the unregistration of agents works correctly.
    """

    with setup_test_agents(2, is_local, prefix="unregister_service") as agents:
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
