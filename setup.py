#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='pymqtt_hass',
    version='1.0',
    description='',
    author='Cyril DUTRIEUX',
    author_email='',
    url='',
    packages=find_packages(),
    entry_points ={
        'console_scripts': [
            'pymqtt_hass_resolv = pymqtt_hass.resolv_config:main'
        ]
    },
)
