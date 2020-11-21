#!/bin/sh
echo "Just in case install dependencies"
sudo apt-get install libcap2-bin
echo "source: "
readlink -f /srv/homeassistant/bin/python
echo "setcapping now"
sudo setcap cap_net_raw,cap_net_admin+eip `readlink -f /srv/homeassistant/bin/python`
echo "now it has following caps:"
getcap `readlink -f /srv/homeassistant/bin/python`
