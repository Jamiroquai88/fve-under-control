#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2024
# Author: Jan Profant <jan@konversation.ai>
# All Rights Reserved

import asyncio  # Library for running asynchronous operations
import datetime  # Module to handle date and time
import random  # Module to generate random numbers
import time  # Module for time-related functions
import logging  # Module for logging

from goodwe import OperationMode  # Import OperationMode enum from goodwe library
from energy_flow.task_control import sleep_routine
from .goodwe_utils import set_operation_mode, get_battery_level  # Custom utilities to interact with GoodWe inverters
from .ote import get_current_prices  # Custom utility to get current energy prices

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Define a dictionary mapping charge hours to battery levels
CHARGE_HOURS = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,  # Always charge for at least 3 hours a day
    4: 40,  # Charge if battery level is above 40%
    5: 60,
    6: 80
}

OTE_ATTEMPTS = 10  # Number of attempts to retrieve OTE data
LOG_INTERVAL = 3  # Interval for logging the status of the battery
MODE = 'buy'  # Operation mode - 'buy' or 'sell'


def battery_charging_task(stop_event,
                          inverter_ip_address,
                          charge_threshold_eur,
                          battery_upper_level,
                          max_charge_hours_key,
                          gradient_threshold,
                          local_extreme_hours_window):
    """
    This function manages the battery charging process based on the current battery level,
    energy prices, and other parameters. It runs in a loop until the `stop_event` is set.

    :param stop_event: threading.Event object used to signal stopping of the task
    :param inverter_ip_address: IP address of the inverter
    :param charge_threshold_eur: Price threshold below which charging should occur
    :param battery_upper_level: Maximum battery level for charging to continue
    :param max_charge_hours_key: Key from CHARGE_HOURS dict determining max charging hours
    :param gradient_threshold: Threshold for price gradient to decide charging
    :param local_extreme_hours_window: Time window to consider for local price minima
    """

    logging.info("Battery subroutine in progress...")

    # Initialize variables for daily operations
    last_day, prices, local_minima, gradients = None, None, None, None
    i = 0  # Counter for logging intervals

    while not stop_event.is_set():  # Main loop that runs until stop_event is set
        today = datetime.date.today().strftime('%Y-%m-%d')  # Get today's date
        if last_day != today:  # Check if prices need to be updated
            prices, local_minima, local_maxima, gradients = get_current_prices(
                today)  # Fetch today's prices and analysis
            last_day = today  # Update the last processed day

        battery_level = asyncio.run(get_battery_level(inverter_ip_address))  # Get current battery level asynchronously
        price_idx = datetime.datetime.now().hour  # Get the current hour index for pricing
        price_now = prices[price_idx]  # Get the current energy price
        sorted_price_idx = sorted(prices).index(price_now)  # Determine the sorted index of the current price

        if 'buy' in MODE:  # If the mode is set to 'buy'
            if battery_level < battery_upper_level:  # Only charge if battery level is below the upper limit
                # Check for local minima in prices and if it makes sense to charge
                is_local_minima = price_idx in local_minima and price_now < min(
                    prices[price_idx + 1:price_idx + local_extreme_hours_window + 1])

                # Decide to charge based on current price, local minima, gradient, and charge hours policy
                if ((price_now < charge_threshold_eur) or is_local_minima or
                        (sorted_price_idx < max_charge_hours_key and battery_level > CHARGE_HOURS[sorted_price_idx])):
                    asyncio.run(set_operation_mode(inverter_ip_address,
                                                   OperationMode.ECO_CHARGE))  # Set inverter to charge mode
                    if i % LOG_INTERVAL == 0:  # Log status every LOG_INTERVAL iterations
                        logging.info(f'Battery level: {battery_level}%, current price {price_now}, will charge now.')
                else:
                    asyncio.run(
                        set_operation_mode(inverter_ip_address, OperationMode.GENERAL))  # Set inverter to general mode
                    if i % LOG_INTERVAL == 0:  # Log status every LOG_INTERVAL iterations
                        logging.info(f'Battery level: {battery_level}%, current price {price_now}, will not charge.')
            else:
                asyncio.run(set_operation_mode(inverter_ip_address,
                                               OperationMode.GENERAL))  # Stop charging if battery is above upper level
        elif 'sell' in MODE:  # Placeholder for 'sell' mode
            raise NotImplementedError  # Not yet implemented

        i += 1  # Increment counter for logging

        if not sleep_routine(stop_event):
            asyncio.run(
                set_operation_mode(inverter_ip_address, OperationMode.GENERAL))  # Set inverter to default mode
            logging.info(f'Battery level: {battery_level}%, charging will stop now.')
            return  # Exit function