#!/usr/bin/env python3
import sys, os
import re
import argparse
import json
import random
import uuid
import logging

from .items import get_device_topic

# https://stackoverflow.com/questions/7016056/python-logging-not-outputting-anything
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('pymqtt_hass')

def run(**kwargs):
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
    device_topic = get_device_topic(jdata['device'])

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

def main():
    logger.setLevel('DEBUG')

    parser = argparse.ArgumentParser()
    parser.add_argument('template')
    args = parser.parse_args()

    run(**vars(args))

