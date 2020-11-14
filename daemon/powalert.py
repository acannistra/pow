import requests
import signal
import os
from time import sleep
import click
import sys
import json
import logging
import RPi.GPIO as g

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

def setup_gpio(pin):
    g.setmode(g.BCM)
    g.setup(pin, g.OUT, initial=g.LOW)

def turn_lamp_on(pin):
    g.output(pin, g.HIGH)
    return True
def turn_lamp_off(pin):
    g.output(pin, g.LOW)
    return False

def die_gracefully(signal, frame):
    turn_lamp_off(POW_GPIO_PIN)
    g.cleanup()
    sys.exit(0)


@click.command()
@click.option('--logfile', default=None)
@click.argument('config')
def daemon(logfile, config):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, filename=logfile)
    params = json.load(open(config))

    setup_gpio(POW_GPIO_PIN)
    signal.signal(signal.SIGINT, die_gracefully)
    signal.signal(signal.SIGTERM, die_gracefully)

    lamp_on = False

    while True:
        is_pow = get_status(params['station'], params['threshold'], params['period'])
    
        if is_pow and not lamp_on:
            logging.info(f"POW! Turning lamp on.")
            lamp_on = turn_lamp_on(POW_GPIO_PIN)
        elif not is_pow and lamp_on: 
            logging.info("Turning lamp off.")
            lamp_on = turn_lamp_off(POW_GPIO_PIN)
        else:
            logging.info(f"Doing nothing. (is_pow = {is_pow}, lamp_on = {lamp_on})")


        logging.info(f"Sleeping for {params['poll_interval_s']} seconds.")
        sleep(params['poll_interval_s'])





if __name__ == '__main__':
    daemon()
