import requests
import os
import click
import sys
import json
import logging

sys.path.append('..')

POW_API_URL = os.environ.get("POW_API_URL", "https://81s7s0fg1e.execute-api.us-west-2.amazonaws.com/dev/pow")
POW_GPIO_PIN = os.environ.get("POW_GPIO_PIN", 21)

def get_status(station, threshold, period):
    params = {
        'station': station,
        'threshold':  threshold,
        'period': period
    }
    logging.info(f"Getting pow status for {station} (threshold: {threshold}, period: {period})...")
    r = requests.get(POW_API_URL, params=params)
    logging.info(f"API Response: {r.json()}")
    return r.json()['is_pow']


@click.command()
@click.argument('config')
@click.argument("gpio", default=POW_GPIO_PIN)
def daemon(config, gpio):
    logging.basicConfig(level=logging.INFO)
    params = json.load(open(config))

    while True:
        status = get_status(params['station'], params['threshold'], params['period'])

        sleep(params['poll_interval_s'])





if __name__ == '__main__':
    daemon()
