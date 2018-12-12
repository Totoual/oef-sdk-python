# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.
from logging import Logger, CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET, StreamHandler, NullHandler

import pytest
from oef.logger import set_logger


@pytest.mark.parametrize("logging_level", [CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET])
@pytest.mark.parametrize("handlers", [[StreamHandler()], [NullHandler()], None])
def test_set_logger(logging_level, handlers):
    """Test that the ``set_logger`` utility function behaves as expected."""
    logger = set_logger("oef", level=logging_level, handlers=handlers)

    assert isinstance(logger, Logger)
    assert logging_level == logger.level

    if handlers:
        assert logger.handlers == handlers
    else:
        assert len(logger.handlers) == 1
        assert type(logger.handlers[0]) == StreamHandler



