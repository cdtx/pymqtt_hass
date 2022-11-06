#!/usr/bin/env python3
import sys, os
import re
import argparse
import json
import uuid
import logging

# https://stackoverflow.com/questions/7016056/python-logging-not-outputting-anything
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('pymqtt_hass')

from paho.mqtt.client import Client
from hass import Device

def get_device_topic(data):
    return '/'.join([
        data['device']['manufacturer'],
        data['device']['model'],
        data['device']['identifiers'],
    ])

def call_config(**kwargs):
    ''' Resolve and print the configuration template
    '''
    template = os.path.expanduser(kwargs['template'])
    if not os.path.exists(template):
        raise FileNotFoundError(template)

    # Load the template as a json structure
    jdata = None
    with open(template, 'r') as fin:
        jdata = json.load(fin)

    # Get device id in json data, or generate a new one
    device_uuid = str(uuid.uuid4())
    device_id = jdata['device']['identifiers'].format(device_id=device_uuid)
    # Replace device_id into the json data
    jdata['device']['identifiers'] = device_id

    # Now, generate the base mqtt topic
    device_topic = get_device_topic(jdata)

    device_data = {
        'device_id':device_id, 
        'device_topic':device_topic,
    }

    # Update all device keys with the whole dataset
    for key, value in jdata['device'].items():
        if isinstance(value, str):
            jdata['device'][key] = value.format(**device_data)


    # Generate ids for each entity
    for entity in jdata['entities']:
        # Get id for this entity, or generate a new one
        entity_uuid = str(uuid.uuid4())
        entity_id = entity['unique_id'].format(entity_id=entity_uuid)
        # Replace entity_id into the json data
        entity['unique_id'] = entity_id
        
        # Then update all entity keys with the whole dataset
        for key, value in entity.items():
            if isinstance(value, str):
                entity[key] = value.format(**device_data, entity_id=entity_id)

        print(json.dumps(jdata, indent=4))
        
def on_connect(*args, **kwargs):
    logger.debug('on_connect')

def call_run(**kwargs):
    config_file_path = os.path.expanduser(kwargs['config'])
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(config_file_path)

    jdata = None
    with open(config_file_path, 'r') as fin:
        jdata = json.load(fin)

    client = Client()
    # Set the client options
    client.on_connect = on_connect
    client.enable_logger()
    client.username_pw_set('mqtt', 'mqtt')
    # Connect the mqtt client
    client.connect('192.168.1.19')
    client.loop()

    device = Device(client, jdata)
    device.send_discovery()
    client.loop()

    # Send sensor value
    topic = '/'.join([
        get_device_topic(jdata),
        'value'
    ])
    payload = uuid.uuid4().int

    logger.debug('Publish [{}] on [{}]'.format(payload, topic))
    client.publish(topic, payload)
    client.loop()



if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()

    logger.setLevel('DEBUG')

    subparsers = main_parser.add_subparsers()

    parser_config = subparsers.add_parser('config')
    parser_config.add_argument('template')
    parser_config.set_defaults(func=call_config)

    parser_run = subparsers.add_parser('run')
    parser_run.add_argument('config')
    parser_run.set_defaults(func=call_run)

    args = main_parser.parse_args()
    args.func(**vars(args))
