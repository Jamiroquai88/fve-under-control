#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2024
# Author: Jan Profant <jan@konversation.ai>
# All Rights Reserved

import asyncio  # For running asynchronous operations
import time  # For time-related functions
import logging  # For logging
from random import random  # Random number generator

from components.goodwe_utils import get_pv_running_mean, get_battery_level  # Custom utilities for GoodWe inverters
from components.tapo_utils import turn_on_off  # Utility to control Tapo devices
from energy_flow.task_control import sleep_routine  # Utility for handling sleep routines

# Constants for controlling boiler behavior based on battery and PV levels
BOJLER_ENABLE_BATTERY_LEVEL = 60  # Minimum battery level to consider turning on the boiler (%)
BATTERY_ALMOST_FULL = 85  # Battery level considered almost full (%)

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def boiler_task(stop_event, inverter_ip_address, tapo_ip_address, consumption):
    """
    Task to manage the operation of a boiler based on battery level and photovoltaic (PV) power generation.
    This task runs continuously until `stop_event` is set.

    :param stop_event: threading.Event object used to signal when to stop the task
    :param inverter_ip_address: IP address of the inverter to get PV and battery data
    :param tapo_ip_address: IP address of the Tapo device to control the boiler
    :param consumption: Power consumption of the boiler in watts
    """

    # Log the start of the boiler subroutine
    logging.info("Boiler subroutine in progress...")

    last_bojler_state = None  # Variable to track the last state of the boiler (on/off)

    while not stop_event.is_set():  # Loop until stop_event is triggered

        # Fetch the current PV power (ppv) and house consumption asynchronously
        ppv, house_consumption = asyncio.run(get_pv_running_mean(inverter_ip_address))

        # Fetch the current battery level asynchronously
        battery_level = asyncio.run(get_battery_level(inverter_ip_address))

        # Log the current battery level, PV power, and house consumption
        logging.info(f'Battery level: {battery_level}%, current ppv: {ppv}, house consumption: {house_consumption}.')

        # Decision logic to turn the boiler on/off based on power conditions
        if ((ppv - house_consumption > consumption) or
                (ppv - house_consumption > consumption / 2 and battery_level > BOJLER_ENABLE_BATTERY_LEVEL) or
                (battery_level > BATTERY_ALMOST_FULL)):

            # Turn on the boiler if the conditions are met and it wasn't already on
            if last_bojler_state is not True:
                turn_on_off(True, ip_address=tapo_ip_address)  # Turn on the boiler
            last_bojler_state = True  # Update the boiler state to "on"

        else:
            # Turn off the boiler if the conditions are not met and it wasn't already off
            if last_bojler_state is not False:
                turn_on_off(False, ip_address=tapo_ip_address)  # Turn off the boiler
            last_bojler_state = False  # Update the boiler state to "off"

        # Sleep for a random interval or until stop_event is set
        if not sleep_routine(stop_event):
            # Log stopping of the boiler task and turn off the boiler
            logging.info(
                f'Boiler will stop now. '
                f'Battery level: {battery_level}%, current ppv: {ppv}, house consumption: {house_consumption}.')
            turn_on_off(False, ip_address=tapo_ip_address)  # Ensure boiler is turned off
            return  # Exit the task