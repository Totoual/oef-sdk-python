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

oef.helpers
~~~~~~~~~~

This module contains helper functions.

"""


import math
from math import sin, cos, sqrt, asin


def to_radians(n: float) -> float:
    """
    From an angle in degrees to an angle in radians

    :param n: the angle in degrees.
    :return: the angle in radians.
    """
    return math.pi/180*n


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute the Haversine distance between two locations (i.e. two pairs of latitude and longitude).

    :param lat1: the latitude of the first location.
    :param lon1: the longitude of the first location.
    :param lat2: the latitude of the second location.
    :param lon2: the longitude of the second location.
    :return: the Haversine distance.
    """

    lon1, lat1 = to_radians(lon1), to_radians(lat1)
    lon2, lat2 = to_radians(lon2), to_radians(lat2)

    # average earth radius
    R = 6372.8

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    computation = asin(sqrt(sin(dlat / 2) * sin(dlat / 2) + cos(lat1) * cos(lat2) * sin(dlon/ 2) * sin(dlon / 2)))
    d = R * computation

    return d
