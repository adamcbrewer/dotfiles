#!/bin/bash

input=$(cat)
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty')

if [ -z "$transcript_path" ] || [ ! -f "$transcript_path" ]; then
  exit 0
fi

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

[ ${#agent_parts[@]} -eq 0 ] && [ ${#skill_parts[@]} -eq 0 ] && exit 0

output="📊"
if [ ${#agent_parts[@]} -gt 0 ]; then
  IFS=', '; output+=" Agents: ${agent_parts[*]}"
fi
if [ ${#skill_parts[@]} -gt 0 ]; then
  [ ${#agent_parts[@]} -gt 0 ] && output+=" |"
  IFS=', '; output+=" Skills: ${skill_parts[*]}"
fi

echo "$output"
exit 0
