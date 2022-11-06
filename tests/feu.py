#!/usr/bin/env python3
import sys, os
import re
import argparse
import json
import random
import uuid
import logging

from paho.mqtt.client import Client

from pymqtt_hass.items import Device

# https://stackoverflow.com/questions/7016056/python-logging-not-outputting-anything
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('pymqtt_hass')
        
def on_connect(*args, **kwargs):
    logger.debug('on_connect')

def run(**kwargs):
    client = Client()
    # Set the client options
    client.on_connect = on_connect
    client.enable_logger()
    client.username_pw_set('mqtt', 'mqtt')
    # Connect the mqtt client
    client.connect('192.168.1.19')
    client.loop()

    device = Device(client, kwargs['hass_config'])
    device.send_discovery()
    client.loop()

    # Send sensor value
    logger.debug('Send sensor value')
    topic = '/'.join([
        device.get_device_topic(),
        'value'
    ])

    payload = int(10000 * random.random())

    logger.debug('Publish [{}] on [{}]'.format(payload, topic))
    client.publish(topic, payload)
    client.loop()



if __name__ == '__main__':
    logger.setLevel('DEBUG')

    parser = argparse.ArgumentParser()
    parser.add_argument('hass_config')

    args = parser.parse_args()
    run(**vars(args))
