#!/bin/sh
#
# Use ipfw to throttle bandwidth.
# usage:
# ./throttle.sh     # Throttle at default (60KB/s)
# ./throttle.sh 5   # Throttle at custom speed (5KB/s)
# ./throttle.sh off # Turn throttling off

# flush rules
ipfw del pipe 1
ipfw del pipe 2
ipfw -q -f flush
ipfw -q -f pipe flush

speed=60
[ ! -z $1 ] && speed=$1

if [ "$1" == "off" ]; then
    echo "disabling BW limit."
    exit
else
    # simulate slow connection <to specific hosts>
    echo "enabling bw limit at ${speed}KByte/s"
    ipfw add pipe 1 ip from any to any
    ipfw add pipe 2 ip from any to any
    ipfw pipe 1 config bw ${speed}KByte/s
    ipfw pipe 2 config bw ${speed}KByte/s
fi