Visit https://www.home-assistant.io/integrations/mqtt/ to learn how to configure discovery

# Introduction

_pymqtt\_hass_ is created to make easy the HomeAssistant's MQTT discovery of any custom made MQTT component.

- It is to use during developpment to build device and entities with unique ids.
- For C code: It is to use during developpment for generating a helper header file.
- For python code: It is to use during device's life to resolv item's topics

# How to use

## Generate config.json
- Write a template based on the one in `tests`
- Run `pymqtt_hass_resolv <template_path> python`

## Generate hass.h
- Run `pymqtt_hass_resolv <template_path> c`

## Use with python code
TBD
