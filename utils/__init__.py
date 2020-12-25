#!/usr/bin/env python
# flake8: noqa
"""Top-level module for mycustomproject ."""
from pkg_resources import DistributionNotFound, get_distribution

from .createcase import xmlpost
from .customLogger import customLogger

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    _version__ = '0.0.0'
