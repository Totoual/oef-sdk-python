# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
from logging import Logger, CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET, StreamHandler, NullHandler

import pytest
from oef.logger import set_logger


@pytest.mark.parametrize("logging_level", [CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET])
@pytest.mark.parametrize("handlers", [[StreamHandler()], [NullHandler()], None])
def test_set_logger(logging_level, handlers):
    logger = set_logger(level=logging_level, handlers=handlers)

    assert isinstance(logger, Logger)
    assert logging_level == logger.level

    if handlers:
        assert logger.handlers == handlers
    else:
        assert len(logger.handlers) == 1
        assert type(logger.handlers[0]) == StreamHandler



