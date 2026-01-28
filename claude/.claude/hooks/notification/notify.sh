#!/bin/bash

input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // empty')
message=$(echo "$input" | jq -r '.message // empty')
notification_type=$(echo "$input" | jq -r '.notification_type // empty')
project=$(basename "${cwd:-unknown}")

case "$notification_type" in
  idle_prompt)        emoji="💤" ;;
  elicitation_dialog) emoji="❓" ;;
  permission_prompt)  emoji="🔐" ;;
  *)                  emoji="👋" ;;
esac

notify-send "Claude · $project" "$emoji ${message:-Needs your attention}" --icon=dialog-information -t 10000
