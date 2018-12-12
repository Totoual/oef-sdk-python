# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.

"""
Python SDK for OEF Agent development.
"""

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())


# TODO add contextmanager for launching OEF Node as subprocess.
# TODO add CONTRIBUTING.rst
# TODO add Makefile
# TODO check README
# TODO check HISTORY (version number)

