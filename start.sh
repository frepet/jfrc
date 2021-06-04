#!/bin/bash
printf "Activating venv\n"
. venv/bin/activate

printf "Starting ServoBlaster\n"
sudo servod --min=500us --max=1000us --cycle-time=10000us

printf "Starting JF-RC\n"

trap 'kill %1; kill %2' SIGINT
printf "Stopping JF-RC\n"
python jfrc_video_server.py & python jfrc_server.py

printf "Stopping ServoBlaster\n"
sudo killall servod

printf "Deactivating venv\n"
deactivate
