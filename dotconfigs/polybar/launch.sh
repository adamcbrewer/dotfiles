#!/usr/bin/env bash

# Terminate already running bar instances
killall polybar

# Wait until the processes have been shut down
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

# get the last listed monitor (hopefully the secondary one)
MONITOR=$(polybar -M | grep -v primary | cut -d ':' -f 1)

# Launch polybar
polybar main &
