# Copyright (C) Fetch.ai 2018 - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import logging

_DEFAULT_LOG_FORMAT = '[%(asctime)s][%(name)s][%(funcName)s][%(levelname)s] %(message)s'


def set_logger(name="oef", level=logging.INFO, handler: logging.Handler=None):
    """
    Utility to set up a logger for the `oef` package.
    :param name: the name of the module you want to activate the logger.
    :param level: the logging level
    :param handler: the logging handler. If None, then a default handler is provided, printing to standard error.
    :return:
    """

    # Make the logger
    logger = logging.getLogger(name)

    # Set its level.
    logger.setLevel(level)

    # Make the handler and attach it.
    if not handler:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(_DEFAULT_LOG_FORMAT)
        handler.setFormatter(formatter)

    logger.handlers = [handler]
