# [ruuvi-HASS.io](https://github.com/ruuvi-friends/ruuvi-hass.io)
RuuviTag sensor for hass.io

This project leverages python3 native bluetooth sockets. For python to have access to the Bluetooth socket family it needs to have been compiled with either lib-bluetooth.h or bluez.h in your operating system.

Recent operating systems like Ubuntu and Raspian should support this when using python3. HASS.io also works after [this pull request](https://github.com/home-assistant/docker-base/pull/53) as well as the official python library [after this pull request](https://github.com/docker-library/python/pull/445)


# Quickstart

Note: If you're not using HASS.io official image, please check bellow the pre-requisites before continuing.

How to get started:

1. Copy the contents of `custom_components` in this repo to `<config folder>/custom_components` (but do **not** change `configuration.yaml` yet).
2. Restart HA to install the custom component and all the dependencies.
3. Add the sensors to `configuration.yaml` according to the instructions bellow.
4. Restart HA again

## Configuration

The configuration.yaml has to be edited like this
```
sensor:
  - platform: ruuvi
    sensors:
        - mac: 'MA:CA:DD:RE:SS:00'
          name: 'livingroom'
        
        - mac: 'MA:CA:DD:RE:SS:01'
          name: 'bathroom'
```

**⚠️ Important note:** Do not add more than one ruuvi platform per adapter in the sensors configuration. 
The code in `setup_platform` is called once per platform, so at boot time multiple blocking requests to IO will be performed, 
resulting in only one of the platforms beings successfully setup.

### Different bluetooth devices
The hass component supports passing the bluetoth adapter.
```
  - platform: ruuvi
    sensors:
        - mac: 'MA:CA:DD:RE:SS:00'
          name: 'livingroom'
    adapter: "hci0"
```
Adapter defaults to the default of ble library

### Throttling state updates
Because we're getting data from the devices every second or so (and updating HomeAssistand database every seconds) this can greatly impact the lifespan of your SD card and storage device (eg. Raspberry pi). As a compromise, we're only updating the sensor's state every 10 seconds. Howver you can change this value by passing a value to the `max_update_frequency` as you please. Eg. 0 will update HomeAssistant state as soon as the new data arrives and not lose any data, 10 will discard all data recieved 10 seconds after each sensor update.

```
  - platform: ruuvi
    sensors:
        - mac: 'MA:CA:DD:RE:SS:00'
          name: 'livingroom'
    max_update_frequency: 5
```

---
# Non HASS.io installations
You might choose to install Homeassistant directly on your machine or through other methods other than the official HASS image. If you do so, here are some pointers to make this custom component work.

## For debian or similar
Run bleson-setcap.sh if you have installed homeassistant to debian/similar according to default instructions. Requires sudo access!
## Homeassistant with Virtual Environment (venv)
(https://www.home-assistant.io/docs/installation/virtualenv/)

1. Install bleson https://github.com/TheCellule/python-bleson

2. Give python superuser permissions so btle scans become possible
```
#Make sure you have setcap
sudo apt install libcap2-bin

#Activate virtual environment, make sure to use proper path according to your installation
~$> source /xx/bin/activate

#Use the python version you've built your venv with! These apply to python3 & default homeassistant venv installation paths etc
~$> which pythonX 
/srv/homeassistant/bin/python3

#Find actual executable
~$> readlink -f /srv/homeassistant/bin/python3
/usr/bin/python3.8 

#Give permissions
~$> sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/python3.8
```

# Tested with
* rasperry pi 4 running Hassio (4 ruuvi sensors)
* raspberry pi 3b+ with homeassistant venv installation and 6 sensors
* Intel NUC with homeassistant venv installation and 6 sensors
* (add please reach out so I'll your setup here)

# Contributors 
This work is a mesh of multiple projects that have been refactored for use in HASS.

- Adding native python bluetooth sockets in HASS base python image - https://github.com/home-assistant/docker-base/pull/53
- Refactoring and reuse of some code from https://github.com/ttu/ruuvitag-sensor to create https://github.com/sergioisidoro/simple-ruuvitag
- Refactoring the work from https://github.com/JonasR-/ruuvi_hass to support bluezson

## Big thanks to:
* [Tomi Tuhkanen](https://github.com/ttu) for all the work in ruuvitag-sensor lib
* [peltsippi](https://github.com/peltsippi)
* [JonasR-](https://github.com/JonasR-)
* [perapp](https://github.com/perapp)
* [rkallensee](https://github.com/rkallensee)