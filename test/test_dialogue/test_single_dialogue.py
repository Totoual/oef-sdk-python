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

"""
This module contains tests on simple usage of the DialogueAgent.
"""

import asyncio

import pytest

from oef.proxy import OEFNetworkProxy, OEFLocalProxy
from test.conftest import _ASYNCIO_DELAY, NetworkOEFNode

from test.test_dialogue.dialogue_agents import SimpleSingleDialogueTest, AgentSingleDialogueTest


class TestRegisterDialogues:
    """Tests about registering and unregistering dialogues."""

    def test_register_dialogue(self):
        """Test that registering a dialogue works correctly."""
        node = OEFLocalProxy.LocalNode()
        agent = AgentSingleDialogueTest(OEFLocalProxy("test_register_dialogue", node))
        dialogue = SimpleSingleDialogueTest(agent, "foo")
        agent.register_dialogue(dialogue)

        assert len(agent.dialogues) == 1
        assert list(agent.dialogues.items())[0] == (dialogue.key, dialogue)

    def test_unregister_dialogue(self):
        """Test that unregistering a dialogue works correctly."""

        node = OEFLocalProxy.LocalNode()
        agent = AgentSingleDialogueTest(OEFLocalProxy("test_register_dialogue", node))
        dialogue = SimpleSingleDialogueTest(agent, "foo")
        agent.register_dialogue(dialogue)
        agent.unregister_dialogue(dialogue)

        assert len(agent.dialogues) == 0

    def test_that_registering_twice_the_same_dialogue_raise_error_local(self):
        """Test that registering twice the same dialogue raises an error."""
        with pytest.raises(ValueError, match="Dialogue key.*already in use"):
            node = OEFLocalProxy.LocalNode()
            agent = AgentSingleDialogueTest(OEFLocalProxy("test_unregister_dialogue", node))
            dialogue = SimpleSingleDialogueTest(agent, "foo")
            agent.register_dialogue(dialogue)
            agent.register_dialogue(dialogue)

    def test_that_unregistering_an_unregistered_dialogue_raise_error_local(self):
        """Test that unregistering a dialogue that has not been registered yet raises an error. (network)"""

        with pytest.raises(ValueError, match="Dialogue key.*not found"):
            node = OEFLocalProxy.LocalNode()
            agent = AgentSingleDialogueTest(OEFLocalProxy("test_unregister_dialogue", node))
            dialogue = SimpleSingleDialogueTest(agent, "foo")
            agent.unregister_dialogue(dialogue)


class TestSimpleMessage:

    def test_on_message_network(self, oef_addr, oef_port):
        """Test that a dialogue agent can receive and handle a simple message correctly. (network)"""

        with NetworkOEFNode():
            dialogue_agent_0 = AgentSingleDialogueTest(OEFNetworkProxy("dialogue_agent_0", oef_addr, oef_port))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_message(0, 1, "dialogue_agent_0", b"message")

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 1
            assert dialogue.received_msg[0] == (0, b"message")

    def test_on_message_local(self):
        """Test that a dialogue agent can receive and handle a simple message correctly. (local)"""

        with OEFLocalProxy.LocalNode() as node:
            dialogue_agent_0 = AgentSingleDialogueTest(OEFLocalProxy("dialogue_agent_0", node))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_message(0, 1, "dialogue_agent_0", b"message")

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 1
            assert dialogue.received_msg[0] == (0, b"message")


class TestCFP:

    def test_on_cfp_network(self):
        """Test that a dialogue agent can receive and handle a CFP correctly. (network)"""

        with NetworkOEFNode():
            dialogue_agent_0 = AgentSingleDialogueTest(OEFNetworkProxy("dialogue_agent_0", "127.0.0.1"))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_cfp(1, 2, "dialogue_agent_0", 0, None)

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 1
            assert dialogue.received_msg[0] == (1, 0, None)

    def test_on_cfp_local(self):
        """Test that a dialogue agent can receive and handle a CFP correctly. (local)"""

        with OEFLocalProxy.LocalNode() as node:
            dialogue_agent_0 = AgentSingleDialogueTest(OEFLocalProxy("dialogue_agent_0", node))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_cfp(1, 2, "dialogue_agent_0", 0, None)

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 1
            assert dialogue.received_msg[0] == (1, 0, None)


class TestPropose:

    def test_on_propose_as_first_message_gives_an_error_network(self, oef_addr, oef_port):
        """Test that if the dialogue agent sends a propose as first message we get an Error. (network)"""
        with NetworkOEFNode():
            with pytest.raises(KeyError, match="Dialogue key .* not found"):
                dialogue_agent_0 = AgentSingleDialogueTest(OEFNetworkProxy("dialogue_agent_0", oef_addr, oef_port))
                dialogue_agent_0.connect()

                dialogue_agent_0.send_propose(0, 0, "dialogue_agent_0", 0, [])

                asyncio.get_event_loop().run_until_complete(asyncio.wait_for(
                    dialogue_agent_0.async_run(), _ASYNCIO_DELAY))

    def test_on_propose_as_first_message_gives_an_error_local(self):
        """Test that if the dialogue agent sends a propose as first message we get an Error. (local)"""
        with OEFLocalProxy.LocalNode() as node:
            with pytest.raises(KeyError, match="Dialogue key .* not found"):
                dialogue_agent_0 = AgentSingleDialogueTest(OEFLocalProxy("dialogue_agent_0", node))
                dialogue_agent_0.connect()

                dialogue_agent_0.send_propose(0, 0, "dialogue_agent_0", 0, [])

                asyncio.get_event_loop().run_until_complete(asyncio.wait_for(
                    dialogue_agent_0.async_run(), _ASYNCIO_DELAY))

    def test_on_propose_network(self, oef_addr, oef_port):
        """Test that a dialogue agent can receive and handle a Propose correctly. (network)"""
        with NetworkOEFNode():
            dialogue_agent_0 = AgentSingleDialogueTest(OEFNetworkProxy("dialogue_agent_0", oef_addr, oef_port))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_cfp(1, 0, "dialogue_agent_0", 0, None)
            dialogue_agent_0.send_propose(2, 0, "dialogue_agent_0", 1, [])

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 2
            assert dialogue.received_msg[0] == (1, 0, None)
            assert dialogue.received_msg[1] == (2, 1, [])

    def test_on_propose_local(self):
        """Test that a dialogue agent can receive and handle a Propose correctly. (network)"""
        with OEFLocalProxy.LocalNode() as node:
            dialogue_agent_0 = AgentSingleDialogueTest(OEFLocalProxy("dialogue_agent_0", node))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_cfp(1, 0, "dialogue_agent_0", 0, None)
            dialogue_agent_0.send_propose(2, 0, "dialogue_agent_0", 1, [])

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 2
            assert dialogue.received_msg[0] == (1, 0, None)
            assert dialogue.received_msg[1] == (2, 1, [])


class TestAccept:

    def test_on_accept_as_first_message_gives_an_error_network(self, oef_addr, oef_port):
        """Test that if the dialogue agent sends an accept as first message we get an Error."""
        with NetworkOEFNode():
            with pytest.raises(KeyError, match="Dialogue key .* not found"):
                dialogue_agent_0 = AgentSingleDialogueTest(OEFNetworkProxy("dialogue_agent_0", oef_addr, oef_port))
                dialogue_agent_0.connect()

                dialogue_agent_0.send_accept(0, 0, "dialogue_agent_0", 0)

                asyncio.get_event_loop().run_until_complete(asyncio.wait_for(
                    dialogue_agent_0.async_run(), _ASYNCIO_DELAY))

    def test_on_accept_as_first_message_gives_an_error_local(self):
        """Test that if the dialogue agent sends an accept as first message we get an Error."""
        with OEFLocalProxy.LocalNode() as node:
            with pytest.raises(KeyError, match="Dialogue key .* not found"):
                dialogue_agent_0 = AgentSingleDialogueTest(OEFLocalProxy("dialogue_agent_0", node))
                dialogue_agent_0.connect()

                dialogue_agent_0.send_accept(0, 0, "dialogue_agent_0", 0)

                asyncio.get_event_loop().run_until_complete(asyncio.wait_for(
                    dialogue_agent_0.async_run(), _ASYNCIO_DELAY))

    def test_on_propose_network(self, oef_addr, oef_port):
        """Test that a dialogue agent can receive and handle a Accept correctly. (network)"""
        with NetworkOEFNode():
            dialogue_agent_0 = AgentSingleDialogueTest(OEFNetworkProxy("dialogue_agent_0", oef_addr, oef_port))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_cfp(1, 0, "dialogue_agent_0", 0, None)
            dialogue_agent_0.send_propose(2, 0, "dialogue_agent_0", 1, [])
            dialogue_agent_0.send_accept(3, 0, "dialogue_agent_0", 2)

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 3
            assert dialogue.received_msg[0] == (1, 0, None)
            assert dialogue.received_msg[1] == (2, 1, [])
            assert dialogue.received_msg[2] == (3, 2)

    def test_on_propose_local(self):
        """Test that a dialogue agent can receive and handle a Accept correctly. (local)"""
        with OEFLocalProxy.LocalNode() as node:
            dialogue_agent_0 = AgentSingleDialogueTest(OEFLocalProxy("dialogue_agent_0", node))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_cfp(1, 0, "dialogue_agent_0", 0, None)
            dialogue_agent_0.send_propose(2, 0, "dialogue_agent_0", 1, [])
            dialogue_agent_0.send_accept(3, 0, "dialogue_agent_0", 2)

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 3
            assert dialogue.received_msg[0] == (1, 0, None)
            assert dialogue.received_msg[1] == (2, 1, [])
            assert dialogue.received_msg[2] == (3, 2)


class TestDecline:

    def test_on_decline_as_first_message_gives_an_error_network(self, oef_addr, oef_port):
        """Test that if the dialogue agent sends an accept as first message we get an Error. (network)"""
        with NetworkOEFNode():
            with pytest.raises(KeyError, match="Dialogue key .* not found"):
                dialogue_agent_0 = AgentSingleDialogueTest(OEFNetworkProxy("dialogue_agent_0", oef_addr, oef_port))
                dialogue_agent_0.connect()

                dialogue_agent_0.send_decline(0, 0, "dialogue_agent_0", 0)

                asyncio.get_event_loop().run_until_complete(asyncio.wait_for(
                    dialogue_agent_0.async_run(), _ASYNCIO_DELAY))

    def test_on_decline_as_first_message_gives_an_error_local(self):
        """Test that if the dialogue agent sends an accept as first message we get an Error. (local)"""
        with OEFLocalProxy.LocalNode() as node:
            with pytest.raises(KeyError, match="Dialogue key .* not found"):
                dialogue_agent_0 = AgentSingleDialogueTest(OEFLocalProxy("dialogue_agent_0", node))
                dialogue_agent_0.connect()

                dialogue_agent_0.send_decline(0, 0, "dialogue_agent_0", 0)

                asyncio.get_event_loop().run_until_complete(asyncio.wait_for(
                    dialogue_agent_0.async_run(), _ASYNCIO_DELAY))

    def test_on_decline_network(self, oef_addr, oef_port):
        """Test that a dialogue agent can receive and handle a Accept correctly. (network)"""
        with NetworkOEFNode():
            dialogue_agent_0 = AgentSingleDialogueTest(OEFNetworkProxy("dialogue_agent_0", oef_addr, oef_port))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_cfp(1, 0, "dialogue_agent_0", 0, None)
            dialogue_agent_0.send_propose(2, 0, "dialogue_agent_0", 1, [])
            dialogue_agent_0.send_decline(3, 0, "dialogue_agent_0", 2)

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 3
            assert dialogue.received_msg[0] == (1, 0, None)
            assert dialogue.received_msg[1] == (2, 1, [])
            assert dialogue.received_msg[2] == (3, 2)

    def test_on_decline_local(self):
        """Test that a dialogue agent can receive and handle a Accept correctly. (local)"""
        with OEFLocalProxy.LocalNode() as node:
            dialogue_agent_0 = AgentSingleDialogueTest(OEFLocalProxy("dialogue_agent_0", node))
            dialogue_agent_0.connect()

            dialogue_agent_0.send_cfp(1, 0, "dialogue_agent_0", 0, None)
            dialogue_agent_0.send_propose(2, 0, "dialogue_agent_0", 1, [])
            dialogue_agent_0.send_decline(3, 0, "dialogue_agent_0", 2)

            asyncio.ensure_future(dialogue_agent_0.async_run())
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_ASYNCIO_DELAY))

            assert len(dialogue_agent_0.dialogues) == 1
            dialogue = next(iter(dialogue_agent_0.dialogues.values()))  # type: SimpleSingleDialogueTest

            assert len(dialogue.received_msg) == 3
            assert dialogue.received_msg[0] == (1, 0, None)
            assert dialogue.received_msg[1] == (2, 1, [])
            assert dialogue.received_msg[2] == (3, 2)

