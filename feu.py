#!/usr/bin/env python3
import sys, os
import re
import argparse
import json
import uuid

def get_device_topic(data):
    return '/'.join([
        data['device']['manufacturer'],
        data['device']['model'],
        data['device']['id'],
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
    device_id = jdata['device']['id'].format(device_id=device_uuid)
    # Replace device_id into the json data
    jdata['device']['id'] = device_id

    # Now, generate the base mqtt topic
    device_topic = get_device_topic(jdata)

    device_data = {
        'device_id':device_id, 
        'device_topic':device_topic,
    }

    # Generate ids for each entity
    for entity in jdata['entities']:
        # Get id for this entity, or generate a new one
        entity_uuid = str(uuid.uuid4())
        entity_id = entity['id'].format(entity_id=entity_uuid)
        # Replace entity_id into the json data
        entity['id'] = entity_id
        
        # Then update all entity keys with the whole dataset
        for key, value in entity.items():
            entity[key] = value.format(**device_data, entity_id=entity_id)

        print(json.dumps(jdata, indent=4))
        
def call_run(**kwargs):
    pass


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()

    subparsers = main_parser.add_subparsers()

    parser_config = subparsers.add_parser('config')
    parser_config.add_argument('template')
    parser_config.set_defaults(func=call_config)

    parser_run = subparsers.add_parser('run')
    #parser_run.add_argument()
    parser_run.set_defaults(func=call_run)

    args = main_parser.parse_args()
    args.func(**vars(args))
