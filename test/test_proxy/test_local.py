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

"""This module contains tests for the messaging functionalities with the local implementation of the OEF Node."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from oef.agents import Agent
from oef.messages import OEFErrorOperation
from oef.proxy import OEFLocalProxy, OEFConnectionError
from oef.query import Query, Constraint, Eq, Gt
from oef.schema import Description, DataModel, AttributeSchema
from ..common import AgentTest
from ..conftest import _ASYNCIO_DELAY


def test_on_message():
    """Test that we can send and receive a simple message."""

    with OEFLocalProxy.LocalNode() as node:

        msg = b"hello"

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        agent_0.send_message(0, 0, agent_0.public_key, msg)
        agent_0.send_message(0, 0, agent_1.public_key, msg)

        asyncio.ensure_future(asyncio.gather(agent_0.async_run(), agent_1.async_run()))
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.stop()
        agent_1.stop()

        agent_0.disconnect()
        agent_1.disconnect()

        assert len(agent_0.received_msg) == 1
        assert agent_0.received_msg[0] == (0, 0, agent_0.public_key, msg)

        assert len(agent_1.received_msg) == 1
        assert agent_1.received_msg[0] == (0, 0, agent_0.public_key, msg)


def test_on_cfp():
    """
    Test that an agent can send a CFP to another agent, with different types of queries.
    """

    with OEFLocalProxy.LocalNode() as node:

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        asyncio.ensure_future(agent_1.async_run())

        agent_0.send_cfp(0, 0, agent_1.public_key, 0, None)
        expected_message_01 = (0, 0, agent_0.public_key, 0, None)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.send_cfp(0, 1, agent_1.public_key, 0, b"hello")
        expected_message_02 = (0, 1, agent_0.public_key, 0, b"hello")
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.send_cfp(0, 2, agent_1.public_key, 0, Query([Constraint("foo", Eq(0))]))
        expected_message_03 = (0, 2, agent_0.public_key, 0, Query([Constraint("foo", Eq(0))]))
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.stop()
        agent_1.stop()

        agent_0.disconnect()
        agent_1.disconnect()

        assert len(agent_1.received_msg) == 3

        assert expected_message_01 == agent_1.received_msg[0]
        assert expected_message_02 == agent_1.received_msg[1]
        assert expected_message_03 == agent_1.received_msg[2]


def test_on_propose():
    """
    Test that an agent can send a Propose to another agent, with different types of proposals.
    """
    with OEFLocalProxy.LocalNode() as node:

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        asyncio.ensure_future(agent_1.async_run())

        agent_0.send_propose(0, 0, agent_1.public_key, 0, b"hello")
        expected_message_01 = (0, 0, agent_0.public_key, 0, b"hello")
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.send_propose(0, 0, agent_1.public_key, 0, [])
        expected_message_02 = (0, 0, agent_0.public_key, 0, [])
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.send_propose(0, 0, agent_1.public_key, 0, [Description({})])
        expected_message_03 = (0, 0, agent_0.public_key, 0, [Description({})])
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.send_propose(0, 0, agent_1.public_key, 0, [Description({}), Description({})])
        expected_message_04 = (0, 0, agent_0.public_key, 0, [Description({}), Description({})])
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_1.stop()

        agent_0.disconnect()
        agent_1.disconnect()

        assert len(agent_1.received_msg) == 4

        assert expected_message_01 == agent_1.received_msg[0]
        assert expected_message_02 == agent_1.received_msg[1]
        assert expected_message_03 == agent_1.received_msg[2]
        assert expected_message_04 == agent_1.received_msg[3]


def test_on_accept():
    """
    Test that an agent can send an Accept to another agent.
    """

    with OEFLocalProxy.LocalNode() as node:

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        asyncio.ensure_future(agent_1.async_run())

        agent_0.send_accept(0, 0, agent_1.public_key, 0)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_1.stop()

        agent_0.disconnect()
        agent_1.disconnect()

        assert agent_1.received_msg[0] == (0, 0, agent_0.public_key, 0)

        assert len(agent_1.received_msg) == 1


def test_on_decline():
    """
    Test that an agent can send a Decline to another agent.
    """

    with OEFLocalProxy.LocalNode() as node:

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        asyncio.ensure_future(agent_1.async_run())

        agent_0.send_decline(0, 0, agent_1.public_key, 0)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_1.stop()

        agent_0.disconnect()
        agent_1.disconnect()

        assert len(agent_1.received_msg) == 1

        assert agent_1.received_msg[0] == (0, 0, agent_0.public_key, 0)


def test_on_search_result_services():
    """
    Test that an agent can do a search for services.
    """

    with OEFLocalProxy.LocalNode() as node:

        foo_attr = AttributeSchema("foo", int, False, "A foo attribute.")
        bar_attr = AttributeSchema("bar", str, False, "A bar attribute.")

        dummy_datamodel = DataModel("dummy_datamodel", [foo_attr, bar_attr])
        desc_1 = Description({"foo": 15, "bar": "BAR"}, dummy_datamodel)
        desc_2 = Description({"foo": 5, "bar": "ABC"}, dummy_datamodel)

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))
        agent_2 = AgentTest(OEFLocalProxy("agent_2", node))

        agent_0.connect()
        agent_1.connect()
        agent_2.connect()

        asyncio.ensure_future(agent_0.async_run())

        agent_1.register_service(0, desc_1)
        agent_2.register_service(0, desc_2)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.search_services(0, Query([Constraint("foo", Eq(0))], dummy_datamodel))
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))
        expected_message_01 = (0, [])

        agent_0.search_services(0, Query([Constraint("foo", Gt(10)), Constraint("bar", Gt("B"))], dummy_datamodel))
        expected_message_02 = (0, [agent_1.public_key])
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.search_services(0, Query([Constraint("bar", Gt("A"))], dummy_datamodel))
        expected_message_03 = (0, [agent_1.public_key, agent_2.public_key])
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_1.unregister_service(0, desc_1)
        agent_2.unregister_service(0, desc_2)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.stop()

        agent_0.disconnect()
        agent_1.disconnect()
        agent_2.disconnect()

        assert len(agent_0.received_msg) == 3

        assert expected_message_01 == agent_0.received_msg[0]
        assert expected_message_02 == agent_0.received_msg[1]
        assert expected_message_03 == agent_0.received_msg[2]


def test_on_search_result_agents():
    """
    Test that an agent can do a search for agents.
    """

    with OEFLocalProxy.LocalNode() as node:

        foo_attr = AttributeSchema("foo", int, False, "A foo attribute.")
        bar_attr = AttributeSchema("bar", str, False, "A bar attribute.")
        dummy_datamodel = DataModel("dummy_datamodel", [foo_attr, bar_attr])

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))
        agent_2 = AgentTest(OEFLocalProxy("agent_2", node))

        agent_0.connect()
        agent_1.connect()
        agent_2.connect()

        asyncio.ensure_future(agent_0.async_run())

        agent_1.register_agent(0, Description({"foo": 15, "bar": "BAR"}, dummy_datamodel))
        agent_2.register_agent(0, Description({"foo": 5, "bar": "ABC"}, dummy_datamodel))
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.search_agents(0, Query([Constraint("foo", Eq(0))], dummy_datamodel))
        expected_message_01 = (0, [])
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.search_agents(0, Query([Constraint("foo", Gt(10)), Constraint("bar", Gt("B"))], dummy_datamodel))
        expected_message_02 = (0, [agent_1.public_key])
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.search_agents(0, Query([Constraint("bar", Gt("A"))], dummy_datamodel))
        expected_message_03 = (0, [agent_1.public_key, agent_2.public_key])
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_1.unregister_agent(0)
        agent_2.unregister_agent(0)

        agent_0.stop()

        agent_0.disconnect()
        agent_1.disconnect()
        agent_2.disconnect()

        assert len(agent_0.received_msg) == 3

        assert expected_message_01 == agent_0.received_msg[0]
        assert expected_message_02 == agent_0.received_msg[1]
        assert expected_message_03 == agent_0.received_msg[2]


def test_unregister_agent():
    """
    Test that the unregistration of agents works correctly.
    """
    with OEFLocalProxy.LocalNode() as node:

        dummy_datamodel = DataModel("dummy_datamodel", [AttributeSchema("foo", int, False)])

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        asyncio.ensure_future(agent_0.async_run())

        agent_1.register_agent(0, Description({}, dummy_datamodel))
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))
        agent_1.unregister_agent(0)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.search_agents(0, Query([Constraint("foo", Eq(0))], dummy_datamodel))
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.stop()

        agent_0.disconnect()
        agent_1.disconnect()

        assert (0, []) == agent_0.received_msg[0]
        assert len(agent_0.received_msg) == 1


def test_unregister_service():
    """
    Test that the unregistration of services works correctly.
    """

    with OEFLocalProxy.LocalNode() as node:

        dummy_datamodel = DataModel("dummy_datamodel", [AttributeSchema("foo", int, False)])
        dummy_service_description = Description({}, dummy_datamodel)

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        asyncio.ensure_future(agent_0.async_run())

        agent_1.register_service(0, dummy_service_description)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))
        agent_1.unregister_service(0, dummy_service_description)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.search_services(0, Query([Constraint("foo", Eq(0))], dummy_datamodel))
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.stop()

        agent_0.disconnect()
        agent_1.disconnect()

        assert (0, []) == agent_0.received_msg[0]

        assert len(agent_0.received_msg) == 1


def test_oef_error_when_unregistering_an_unregistered_service():
    """Test that we receive an OEF Error message when we try to unregister a non existing service."""

    with OEFLocalProxy.LocalNode() as node:

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        asyncio.ensure_future(agent_0.async_run())

        agent_0.on_oef_error = MagicMock()
        agent_0.unregister_service(0, Description({"foo": 1}))
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.on_oef_error.assert_called_with(0, OEFErrorOperation.UNREGISTER_SERVICE)

        agent_0.stop()

        agent_0.disconnect()
        agent_1.disconnect()


def test_oef_error_when_failing_in_unregistering_agent():
    """Test that we receive an OEF Error message when we try to unregister a non registered agent."""

    with OEFLocalProxy.LocalNode() as node:

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        asyncio.ensure_future(agent_0.async_run())

        agent_0.on_oef_error = MagicMock()
        agent_0.unregister_agent(0)
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.on_oef_error.assert_called_with(0, OEFErrorOperation.UNREGISTER_DESCRIPTION)

        agent_0.stop()

        agent_0.disconnect()
        agent_1.disconnect()


def test_dialogue_error_when_destination_is_not_connected():
    """Test that we receive an ``DialogueError`` message when we try to send a message to an unconnected agent."""

    with OEFLocalProxy.LocalNode() as node:

        agent_0 = AgentTest(OEFLocalProxy("agent_0", node))
        agent_1 = AgentTest(OEFLocalProxy("agent_1", node))

        agent_0.connect()
        agent_1.connect()

        agent_0.on_dialogue_error = MagicMock()

        asyncio.ensure_future(agent_0.async_run())

        # send a message to an unconnected agent
        agent_0.send_message(0, 0, "unconnected_agent", b"dummy_message")
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent_0.on_dialogue_error.assert_called_with(0, 0, "unconnected_agent")

        agent_0.stop()

        agent_0.disconnect()
        agent_1.disconnect()


def test_connection_error_on_send():
    """Test that a OEFConnectionError is raised when we try to send a message before
    the connection has been established."""
    with OEFLocalProxy.LocalNode() as node:
        with pytest.raises(OEFConnectionError, match="Connection not established yet."):
            proxy = OEFLocalProxy("test_oef_connection_error_when_send", node)
            agent = Agent(proxy)
            agent.send_message(0, 0, proxy.public_key, b"message")


def test_connection_error_on_receive(oef_addr, oef_port):
    """Test that a OEFConnectionError is raised when we try to receive a message before
    the connection has been established."""
    with OEFLocalProxy.LocalNode() as node:
        with pytest.raises(OEFConnectionError, match="Connection not established yet."):
            proxy = OEFLocalProxy("test_oef_connection_error_when_receive", node)
            agent = Agent(proxy)
            agent.run()


def test_that_two_connect_attempts_work_correctly(oef_addr, oef_port):
    """Test that two call to the :func:'~agents.Agent.connect()' method work correctly.
    Use the local implementation of the OEF."""
    with OEFLocalProxy.LocalNode() as node:
        proxy = OEFLocalProxy("two_connect_attempt", node)
        agent_1 = Agent(proxy)
        first_status = agent_1.connect()
        second_status = agent_1.connect()

    assert first_status
    assert second_status


def test_connection_error_public_key_already_in_use(oef_addr, oef_port):
    """Test that a OEFConnectionError is raised when we try to connect two agents with the same public key."""
    with pytest.raises(OEFConnectionError, match="Public key already in use."):
        with OEFLocalProxy.LocalNode() as node:
            proxy_1 = OEFLocalProxy("the_same_public_key", node)
            proxy_2 = OEFLocalProxy(proxy_1.public_key, node)
            agent_1 = Agent(proxy_1)
            agent_2 = Agent(proxy_2)
            agent_1.connect()
            agent_2.connect()


def test_disconnect(oef_addr, oef_port):
    """Test that the disconnect method works correctly."""

    with OEFLocalProxy.LocalNode() as node:
        proxy_1 = OEFLocalProxy("disconnect", node)
        agent_1 = Agent(proxy_1)
        assert not agent_1._oef_proxy.is_connected()
        agent_1.connect()
        assert agent_1._oef_proxy.is_connected()
        agent_1.disconnect()
        assert not agent_1._oef_proxy.is_connected()


def test_more_than_once_async_run_call(oef_addr, oef_port):
    """Test that when we call async_run more than once we get a warning message."""
    with OEFLocalProxy.LocalNode() as node:
        with patch('logging.Logger.warning') as mock:
            proxy = OEFLocalProxy("test_more_than_one_async_run_call", node)
            agent = Agent(proxy)
            agent.connect()

            asyncio.ensure_future(agent.async_run())
            asyncio.ensure_future(agent.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            mock.assert_called_with("Agent {} already scheduled for running.".format(agent.public_key))

            agent.stop()
            agent.disconnect()


def test_send_more_than_64_kilobytes():
    """Test that we can send more than 64KB messages."""
    with OEFLocalProxy.LocalNode() as node:
        proxy = OEFLocalProxy("test_send_more_than_64_kilobytes", node)
        agent = AgentTest(proxy)

        expected_msg_id = 0
        expected_dialogue_id = 0
        expected_content = b"a"*2**16
        expected_origin = agent.public_key

        agent.connect()
        agent.send_message(expected_msg_id, expected_dialogue_id, agent.public_key, expected_content)
        asyncio.ensure_future(agent.async_run())
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

        agent.stop()
        agent.disconnect()

    actual_msg_id, actual_dialogue_id, actual_origin, actual_content = agent.received_msg[0]

    # assert that we received only one message
    assert len(agent.received_msg) == 1

    # assert that the message contains what we've sent.
    assert expected_msg_id == actual_msg_id
    assert expected_dialogue_id == actual_dialogue_id
    assert expected_origin == actual_origin
    assert expected_content == actual_content
