import sys, os
import logging
import json

logger = logging.getLogger('pymqtt_hass')

def get_device_topic(data):
    return '/'.join([
        data['manufacturer'],
        data['model'],
        data['identifiers'],
    ])

class Entity:
    discovery_prefix = 'homeassistant'

    def __init__(self, mqtt_client, data):
        self.client = mqtt_client
        self.config = data

    def discovery_items(self, device):
        topic = '/'.join([
            self.discovery_prefix,
            self.config['component'],
            self.config['unique_id'],
            'config'
        ])
        logger.debug('Computed topic [{}]'.format(topic))

        # The payload must contain data about the device
        payload = json.dumps({**self.config, 'device':device})
        logger.debug('Computed payload :')
        logger.debug(payload)

        return (topic, payload)


    def send_discovery(self, device):
        ''' deprecated, since use may be able to choose it's mqtt client '''
        logger.debug('Send entity discovery {}'.format(self.config['unique_id']))

        topic, payload = self.discovery_items(device)

        self.client.publish(topic, payload)

class Device:
    def __init__(self, mqtt_client, config_file):
        config_file = os.path.expanduser(config_file)
        if not os.path.exists(config_file):
            raise FileNotFoundError(config_file)

        jdata = None
        with open(config_file, 'r') as fin:
            data = json.load(fin)

        self.client = mqtt_client
        self.config = data['device']
        self.entities = [Entity(mqtt_client, d) for d in data['entities']]

    def get_device_topic(self):
        return get_device_topic(self.config)

    def discovery_items(self):
        for entity in self.entities:
            yield entity.discovery_items(self.config)

    def send_discovery(self):
        logger.debug('Send device discovery')
        for entity in self.entities:
            entity.send_discovery(self.config)

