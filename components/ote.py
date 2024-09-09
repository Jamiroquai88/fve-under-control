#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2024
# Author: Jan Profant <jan@konversation.ai>
# All Rights Reserved

import logging
import sys
import time

import lxml.html
import requests

import numpy as np
from scipy.signal import argrelmin, argrelmax


# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

OTE_CR_PAGE = 'https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh?date='
OTE_ATTEMPTS = 10

def get_prices(day, weights=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.9, 0.8, 0.75, 0.75, 0.8, 0.95, 1, 1, 1, 1, 1, 1, 1)):
    url = f'{OTE_CR_PAGE}{day}'
    response = requests.get(url)
    tree = lxml.html.fromstring(response.text)
    table = tree.cssselect('table.report_table')
    assert len(table) == 2
    table = table[1]
    rows = table.cssselect('tbody > tr')
    assert len(rows) == 26 or len(rows) == 25, len(rows)
    rows = rows[:24]
    for idx, row in enumerate(rows):
        cols = row.cssselect('td')
        if len(cols) == 5:
            yield float(cols[0].text_content().replace(' ', '').replace(',', '.')) * weights[idx]

def get_current_prices(today):
    for i in range(OTE_ATTEMPTS):
        try:
            prices = list(get_prices(today, [1 for x in range(24)]))
            local_minima = list(argrelmin(np.array(prices))[0])
            local_maxima = list(argrelmax(np.array(prices))[0])
            gradients = np.gradient(prices)
            logging.info(f'Prices for {today}: {prices} with local minima {local_minima} and local maxima {local_maxima}')
            return prices, local_minima, local_maxima, gradients
        except AssertionError as e:
            logging.info(e)
            time.sleep(60)
    logging.info(f'Failed to get prices from OTE for {OTE_ATTEMPTS} attempts, probably an error occured.')
    sys.exit(1)