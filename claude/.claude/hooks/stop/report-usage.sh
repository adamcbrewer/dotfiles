#!/bin/bash

input=$(cat)
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty')
cwd=$(echo "$input" | jq -r '.cwd // empty')

if [ -z "$transcript_path" ] || [ ! -f "$transcript_path" ]; then
  exit 0
fi

log_file="${cwd:-.}/.claude/usage.ignore.txt"
mkdir -p "$(dirname "$log_file")"

last_prompt=$(jq -r '
  select(.type == "user") |
  .message.content |
  if type == "string" then . else empty end
' "$transcript_path" 2>/dev/null \
  | grep -v -e '<command-' -e '<local-command' -e '^\[Request' -e '^$' \
  | tail -1 \
  | cut -c1-120)

declare -A agents
declare -A skills

while IFS= read -r line; do
  name=$(echo "$line" | jq -r '.type // empty')
  [ "$name" != "tool_use" ] && continue

  tool=$(echo "$line" | jq -r '.name // empty')

  if [ "$tool" = "Task" ]; then
    agent_type=$(echo "$line" | jq -r '.input.subagent_type // "unknown"')
    agents["$agent_type"]=$(( ${agents["$agent_type"]:-0} + 1 ))
  elif [ "$tool" = "Skill" ]; then
    skill_name=$(echo "$line" | jq -r '.input.skill // "unknown"')
    skills["$skill_name"]=$(( ${skills["$skill_name"]:-0} + 1 ))
  fi
done < <(jq -c '.message?.content[]? // empty' "$transcript_path" 2>/dev/null)

agent_parts=()
for key in "${!agents[@]}"; do
  agent_parts+=("$key (${agents[$key]})")
done

skill_parts=()
for key in "${!skills[@]}"; do
  skill_parts+=("$key (${skills[$key]})")
done

output="📊 $(date '+%Y-%m-%d %H:%M')"
if [ ${#agent_parts[@]} -gt 0 ]; then
  IFS=', '; output+=" | Agents: ${agent_parts[*]}"
fi
if [ ${#skill_parts[@]} -gt 0 ]; then
  IFS=', '; output+=" | Skills: ${skill_parts[*]}"
fi

{
  [ -n "$last_prompt" ] && echo "💬 $last_prompt"
  echo "$output"
} > "$log_file"
exit 0
