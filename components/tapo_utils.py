#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2024
# Author: Jan Profant <jan@konversation.ai>
# All Rights Reserved

import logging
import time

from PyP100 import PyP110

username = "YOUR_USERNAME"
password = "YOUR_PASSWORD"

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def turn_on_off(on=True, ip_address=None):
    for i in range(10):
        try:
            p110 = PyP110.P110(ip_address, username, password)  # Creating a P110 plug object

            p110.handshake()  # Creates the cookies required for further methods
            p110.login()  # Sends credentials to the plug and creates AES Key and IV for further methods

            if on:
                p110.turnOn() # Sends the turn on request
                logging.info(f'Turning on.')
            else:
                p110.turnOff()  # Sends the turn off request
                logging.info(f'Turning off.')
            break
        except:
            logging.info(f'Connecting to {ip_address} was not successfull.')
            time.sleep(60)