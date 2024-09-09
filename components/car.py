#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022
# Author: Jan Profant <jan@konversation.ai>
# All Rights Reserved

import subprocess  # Module to execute shell commands
import time  # Module for time-related functions
import asyncio  # Library for running asynchronous operations
import logging  # Module for logging

from components.goodwe_utils import get_pv_running_mean, get_battery_level  # Custom utilities for GoodWe inverters
from energy_flow.task_control import sleep_routine  # Utility for sleep control based on external events

# Constants for the task
MIN_BATTERY_LEVEL = 80  # Minimum battery level required to allow car charging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def car_charging_task(stop_event,
                      inverter_ip_address,
                      max_current_a,
                      min_current_a):
    """
    Task to manage car charging based on photovoltaic (PV) power generation and battery level.
    This function will keep running until the `stop_event` is set.

    :param stop_event: threading.Event object to signal when to stop the task
    :param inverter_ip_address: IP address of the inverter to get PV and battery data
    :param max_current_a: Maximum charging current in amps
    :param min_current_a: Minimum charging current in amps
    """

    # Convert charging current limits from amps to watts
    one_amp = 240 * 3  # Power equivalent of 1 amp in watts (for 240V and 3 phases)
    min_w = min_current_a * one_amp  # Minimum charging power (in watts), considering 240V and 3 phases
    max_w = max_current_a * one_amp  # Maximum charging power (in watts)

    while not stop_event.is_set():  # Main loop, running until stop_event is triggered
        logging.info("Car charging subroutine in progress...")

        # Fetch PV running mean (ppv) and house consumption values asynchronously
        ppv, house_consumption = asyncio.run(get_pv_running_mean(inverter_ip_address))

        # Get current battery level asynchronously
        battery_level = asyncio.run(get_battery_level(inverter_ip_address))

        logging.info(f'Battery level: {battery_level}%, current ppv: {ppv}, house consumption: {house_consumption}.')

        # Condition to enable car charging: PV power surplus and battery level above threshold
        if ppv - house_consumption > min_w and battery_level > MIN_BATTERY_LEVEL:
            # Calculate the number of charging amps based on available surplus power
            charge_amps = (ppv - house_consumption) / one_amp
            logging.info(f'Enabling car charging, charging amps: {charge_amps}')

            # Set charging current and enable charging via EVCC
            subprocess.check_call(f'evcc charger -i {int(charge_amps)}', shell=True)
            subprocess.check_call(f'evcc charger -e', shell=True)
        else:
            # Disable car charging if conditions are not met
            subprocess.check_call(f'evcc charger -d', shell=True)

    # If stop_event is set, stop car charging gracefully
    if not sleep_routine(stop_event):
        logging.info(
            f'Car charging will stop now. '
            f'Battery level: {battery_level}%, current ppv: {ppv}, house consumption: {house_consumption}.')
        subprocess.check_call(f'evcc charger -d', shell=True)  # Disable car charging
        return  # Exit the task