#!/bin/bash

input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // empty')
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty')
project=$(basename "${cwd:-unknown}")

duration=""
if [ -n "$transcript_path" ] && [ -f "$transcript_path" ]; then
  first_ts=$(jq -r 'select(.type == "user" and .timestamp) | .timestamp' "$transcript_path" 2>/dev/null | tail -1)
  last_ts=$(jq -r 'select(.type == "assistant" and .timestamp) | .timestamp' "$transcript_path" 2>/dev/null | tail -1)
  if [ -n "$first_ts" ] && [ -n "$last_ts" ]; then
    start_epoch=$(date -d "$first_ts" +%s 2>/dev/null)
    end_epoch=$(date -d "$last_ts" +%s 2>/dev/null)
    if [ -n "$start_epoch" ] && [ -n "$end_epoch" ]; then
      elapsed=$((end_epoch - start_epoch))
      mins=$((elapsed / 60))
      secs=$((elapsed % 60))
      if [ "$mins" -gt 0 ]; then
        duration=" ${mins}m ${secs}s"
      else
        duration=" ${secs}s"
      fi
    fi
  fi
fi

notify-send "Claude · $project" "✅ Done!${duration}" --icon=dialog-information
