import sys, os
import logging
import json

logger = logging.getLogger('pymqtt_hass')

class Entity:
    discovery_prefix = 'homeassistant'

    def __init__(self, mqtt_client, data):
        self.client = mqtt_client
        self.config = data

    def send_discovery(self, device):
        logger.debug('Send entity discovery {}'.format(self.config['unique_id']))
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

        self.client.publish(topic, payload)

class Device:
    def __init__(self, mqtt_client, data):
        self.client = mqtt_client
        self.config = data['device']
        self.entities = [Entity(mqtt_client, d) for d in data['entities']]

    def send_discovery(self):
        logger.debug('Send device discovery')
        for entity in self.entities:
            entity.send_discovery(self.config)

