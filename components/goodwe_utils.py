#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022
# Author: Jan Profant <jan@konversation.ai>
# All Rights Reserved

import logging
import time

import goodwe
import numpy as np
from goodwe import OperationMode

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


async def get_pv_running_mean(inverter_ip_address, running_mean_values=5, running_mean_sleep_seconds=3):
    logging.info(f'Computing pv running mean, it will take {running_mean_values * running_mean_sleep_seconds} seconds')
    ppv_mean, house_consumption_mean = [], []
    inverter = await goodwe.connect(inverter_ip_address)
    for _ in range(running_mean_values):
        runtime_data = await inverter.read_runtime_data()

        for sensor in inverter.sensors():
            if sensor.id_ in runtime_data:
                if sensor.id_ == 'ppv':
                    ppv_mean.append(runtime_data[sensor.id_])
                elif sensor.id_ == 'house_consumption':
                    house_consumption_mean.append(runtime_data[sensor.id_])
        time.sleep(running_mean_sleep_seconds)
    return np.mean(ppv_mean), np.mean(house_consumption_mean)


async def get_battery_level(inverter_ip_address):
    inverter = await goodwe.connect(inverter_ip_address)
    runtime_data = await inverter.read_runtime_data()

    for sensor in inverter.sensors():
        if sensor.id_ in runtime_data and sensor.id_ == 'battery_soc':
            return runtime_data[sensor.id_]


async def set_operation_mode(inverter_ip_address, operation_mode: OperationMode):
    inverter = await goodwe.connect(inverter_ip_address)

    curr_operation_mode = await inverter.get_operation_mode()
    if operation_mode != curr_operation_mode:
        logging.info(f'Setting operation mode {operation_mode} from {curr_operation_mode}')
        await inverter.set_operation_mode(operation_mode)


async def example(inverter_ip_address):
    inverter = await goodwe.connect(inverter_ip_address)
    runtime_data = await inverter.read_runtime_data()

    for sensor in inverter.sensors():
        if sensor.id_ in runtime_data:
            logging.info(f"{sensor.id_}: \t\t {sensor.name} = {runtime_data[sensor.id_]} {sensor.unit}")
