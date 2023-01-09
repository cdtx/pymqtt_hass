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

def print_json_file(jdata):
    print(json.dumps(jdata, indent=4))

def print_h_file(jdata):
    header_content = [
        '#ifndef _HASS_ENTITIES_H_',
        '#define _HASS_ENTITIES_H_',
        '',
    ]

    # Define the base device topic
    device_topic_name = 'HASS_DEVICE_TOPIC'
    device_topic_value = get_device_topic(jdata['device'])
    header_content.append(
        '#define\t{}\t{}'.format(
            device_topic_name,
            '"{}"'.format(device_topic_value),
        )
    )
    
    header_content.append('')

    # Define for all entities:
    # - publish topic
    # - discovery topic and data
    for entity in jdata.get('entities', {}):
        # Entity's publish topic
        publish_topic_name = '{}_{}_{}'.format(
            'HASS_ENTITY',
            entity.get('name', 'unknown').upper(),
            'PUBLISH_TOPIC',
        )
        publish_topic_value = entity['state_topic']
        header_content.append(
            '#define\t{}\t{}'.format(
                publish_topic_name,
                '"{}"'.format(publish_topic_value),
            )
        )

        # Entity's discovery topic
        discovery_topic_name = '{}_{}_{}'.format(
            'HASS_ENTITY',
            entity.get('name', 'unknown').upper(),
            'DISCOVERY_TOPIC',
        )
        discovery_topic_value = '/'.join([
            'homeassistant',
            entity['component'],
            entity['unique_id'],
            'config',
        ])
        header_content.append(
            '#define\t{}\t{}'.format(
                discovery_topic_name,
                '"{}"'.format(discovery_topic_value),
            )
        )

        # Entity's discovery data
        discovery_data_name = '{}_{}_{}'.format(
            'HASS_ENTITY',
            entity.get('name', 'unknown').upper(),
            'DISCOVERY_DATA',
        )

        discovery_data_value = json.dumps({
            **entity,
            'device':jdata['device'],
        }).replace('"', '\\"')

        header_content.append(
            '#define\t{}\t{}'.format(
                discovery_data_name,
                '"{}"'.format(discovery_data_value),
            )
        )
        header_content.append('')

    header_content += [
        '',
        '#endif'
    ]

    print("\n".join(header_content))


def run(**kwargs):
    ''' Resolve and print the configuration template
    '''
    template = os.path.expanduser(kwargs['template'])
    output_type = kwargs['output']
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

    if output_type == 'json':
        print_json_file(jdata)
    elif output_type == 'h':
        print_h_file(jdata)

def main():
    logger.setLevel('DEBUG')

    parser = argparse.ArgumentParser()
    parser.add_argument('template', help='Path to the json template file')
    parser.add_argument('output', choices=['json', 'h'], help='Output format')
    args = parser.parse_args()

    run(**vars(args))

