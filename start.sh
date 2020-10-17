#!/bin/bash
printf "Starting JF-RC\n"

trap 'kill %1; kill %2' SIGINT
python3 jfrc_video_server.py & python3 jfrc_server.py
