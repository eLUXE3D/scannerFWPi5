#!/bin/bash

echo "Hello JM"
pushd /home/pi/Teeth/release2
sudo python3 /home/pi/Teeth/release2/main.py
popd

sleep 180
