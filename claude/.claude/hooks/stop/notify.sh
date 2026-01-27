#!/bin/bash

input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // empty')
project=$(basename "${cwd:-unknown}")

notify-send "Claude · $project" "Task complete, ready for review" --icon=dialog-information
