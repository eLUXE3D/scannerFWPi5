#!/bin/bash

echo "Hello JM"
sleep 10
pushd /home/pi/Teeth/release2
git pull origin master

sudo python3 /home/pi/Teeth/release2/main.py
popd
sleep 180
