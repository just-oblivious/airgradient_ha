# Custom Home Assistant integration for AirGradient devices

## Supported sensors

- AirGradient ONE V9 (ONE-V9)

## Installation through HACS
1. Add a custom repository to HACS:
  - URL: `https://github.com/just-oblivious/airgradient_ha`
  - Type: "Integration"
2. Install "AirGradient";
3. Restart Home Assistant'
4. Continue with device preparation and configuration.


## Device preparation (required!)

By default AirGradient devices post data to a hardcoded HTTP endpoint (`hw.airgradient.com`), this URL needs to be modified to make the sensor talk to Home Assistant.

Follow these instructions to prep your sensors:

1. Setup a development environment as per [AirGradients instructions](https://www.airgradient.com/blog/install-arduino-c3-mini/);
1. Open the Arduino code for your AirGradient device;
1. Patch the `APIROOT` variable and point it to your Home Assistant machine (e.g. `http://192.168.1.10:8088/`);
1. Flash the firmware to your device.


## Configuration

After adding the component to Home Assistant add the "AirGradient" integration and setup a new listener.

Devices are automatically added as soon as they start sending data to the configured port on your Home Assistant host. The default port is `8088`.

*Do not forget to forward the selected port to your Home Assistant container when running in Docker.*
