#!/bin/bash

input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // empty')
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty')

project=$(basename "${cwd:-unknown}")

if [ -z "$transcript_path" ] || [ ! -f "$transcript_path" ]; then
  notify-send "Claude · $project" "Session complete" --icon=dialog-information
  exit 0
fi

task=$(jq -r '
  select(.type == "user") |
  .message.content |
  if type == "string" then . else empty end
' "$transcript_path" 2>/dev/null \
  | grep -v -e '<command-' -e '<local-command' -e '^\[Request' -e '^$' \
  | head -1 \
  | cut -c1-120)

first_ts=$(jq -r 'select(.timestamp) | .timestamp' "$transcript_path" 2>/dev/null | head -1)
last_ts=$(jq -r 'select(.timestamp) | .timestamp' "$transcript_path" 2>/dev/null | tail -1)

duration=""
if [ -n "$first_ts" ] && [ -n "$last_ts" ]; then
  start_epoch=$(date -d "$first_ts" +%s 2>/dev/null)
  end_epoch=$(date -d "$last_ts" +%s 2>/dev/null)
  if [ -n "$start_epoch" ] && [ -n "$end_epoch" ]; then
    elapsed=$((end_epoch - start_epoch))
    mins=$((elapsed / 60))
    secs=$((elapsed % 60))
    if [ "$mins" -gt 0 ]; then
      duration="${mins}m ${secs}s"
    else
      duration="${secs}s"
    fi
  fi
fi

turns=$(jq -c 'select(.type == "assistant")' "$transcript_path" 2>/dev/null | wc -l)

body=""
[ -n "$task" ] && body="$task"
meta=""
[ -n "$duration" ] && meta="⏱ $duration"
[ "$turns" -gt 0 ] && meta="${meta:+$meta · }💬 $turns turns"
[ -n "$meta" ] && body="${body:+$body\n}$meta"

notify-send "Claude · $project" "${body:-Session complete}" --icon=dialog-information
