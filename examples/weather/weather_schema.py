# -*- coding: utf-8 -*-

# Copyright 2018, Fetch AI Ltd. All Rights Reserved.


"""
This module defines the attributes and the data model used by the weather example.
"""

from oef.schema import DataModel, AttributeSchema

WIND_SPEED_ATTR = AttributeSchema("wind_speed",
                                  bool,
                                  is_attribute_required=True,
                                  attribute_description="Provides wind speed measurements.")

TEMPERATURE_ATTR = AttributeSchema("temperature",
                                   bool,
                                   is_attribute_required=True,
                                   attribute_description="Provides temperature measurements.")

AIR_PRESSURE_ATTR = AttributeSchema("air_pressure",
                                    bool,
                                    is_attribute_required=True,
                                    attribute_description="Provides air pressure measurements.")

HUMIDITY_ATTR = AttributeSchema("humidity",
                                bool,
                                is_attribute_required=True,
                                attribute_description="Provides humidity measurements.")


WEATHER_DATA_MODEL = DataModel("weather_data",
                               [WIND_SPEED_ATTR, TEMPERATURE_ATTR, AIR_PRESSURE_ATTR, HUMIDITY_ATTR],
                               "All possible weather data.")
