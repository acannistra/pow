import requests
import signal
import os
from time import sleep
import click
import sys
import json
import logging
import random
import RPi.GPIO as g
from twython import Twython

sys.path.append('..')


TWITTER_PREFIXES = [
    "ITS SNOWING! ",
    "QUIT YOUR DAY JOB! ",
    "HIT THE TUBES! ",
    "WAHOO!",
    "STOP WHAT YOU'RE DOING"
]

def tweet(location, amount, interval, authdata):
    _tw = Twython(
        authdata['consumer_key'],
        authdata['consumer_secret'],
        authdata['access_token_key'],
        authdata['access_token_secret']
    )
    tweet_fmt = "{rand_prefix} POW Light is on! ({location}, {amount}\" in {interval}h)"
    rand_prefix = random.choice(TWITTER_PREFIXES)
    _tweet_str = tweet_fmt.format(
        rand_prefix = rand_prefix,
        location = location,
        amount = amount,
        interval = interval
    )
    _tw.update_status(status=_tweet_str)


POW_API_URL = os.environ.get("POW_API_URL", "https://pow.fly.dev/pow")
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
    return (r.json()['is_pow'] == 'True', r.json())

def setup_gpio(pin):
    g.setmode(g.BCM)
    g.setup(pin, g.OUT, initial=g.HIGH)

def turn_lamp_on(pin):
    g.output(pin, g.LOW)
    return True
def turn_lamp_off(pin):
    g.output(pin, g.HIGH)
    return False

def die_gracefully(signal, frame):
    turn_lamp_off(POW_GPIO_PIN)
    g.cleanup()
    sys.exit(0)

def test_lamp(pin):
    logging.info("Testing lamp") 
    turn_lamp_on(pin)
    logging.info(" lamp on")
    sleep(1)
    turn_lamp_off(pin)
    logging.info(' lamp off')
    return True


@click.command()
@click.option('--logfile', default=None)
@click.option("--twitter", default=None)
@click.argument('config')
def daemon(logfile, twitter, config):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO, filename=logfile)
    params = json.load(open(config))

    setup_gpio(POW_GPIO_PIN)
    signal.signal(signal.SIGINT, die_gracefully)
    signal.signal(signal.SIGTERM, die_gracefully)

    test_lamp(POW_GPIO_PIN)

    twitter_auth = None
    if twitter:
        twitter_auth = json.load(open(twitter))

    lamp_on = False

    while True:
        is_pow, api_data = get_status(params['station'], params['threshold'], params['period'])

        if is_pow and (not lamp_on):
            logging.info(f"POW! Turning lamp on.")
            lamp_on = turn_lamp_on(POW_GPIO_PIN)
            if twitter_auth:
                tweet(params['station'], api_data['period_accumulation'], params['period'], twitter_auth)
        elif not is_pow and lamp_on:
            logging.info("Turning lamp off.")
            lamp_on = turn_lamp_off(POW_GPIO_PIN)
        else:
            logging.info(f"Doing nothing. (is_pow = {is_pow}, lamp_on = {lamp_on})")


        logging.info(f"Sleeping for {params['poll_interval_s']} seconds.")
        sleep(params['poll_interval_s'])





if __name__ == '__main__':
    daemon()
