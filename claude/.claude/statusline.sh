#!/bin/bash

input=$(cat)

model_name=$(echo "$input" | jq -r '.model.display_name // .model.id')
version=$(echo "$input" | jq -r '.version')
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
autocompact_buffer=45000
effective_context=$((context_size - autocompact_buffer))
current_dir=$(echo "$input" | jq -r '.workspace.current_dir')
session_id=$(echo "$input" | jq -r '.session_id // ""')
session_short="${session_id: -6}"

# Try to get accurate context usage from current_usage (API response data)
current_input=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
cache_creation=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
cache_read=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')

# Calculate actual context usage
used_tokens=$((current_input + cache_creation + cache_read))

# If current_usage is empty/zero, fall back to checking for used_tokens field
if [ "$used_tokens" -eq 0 ]; then
    used_tokens=$(echo "$input" | jq -r '.context_window.used_tokens // 0')
fi

# Calculate percentage against effective context (excluding autocompact buffer)
if [ "$effective_context" -gt 0 ] && [ "$used_tokens" -gt 0 ]; then
    used_pct=$((used_tokens * 100 / effective_context))
else
    used_pct=0
fi

model_short="$model_name"
if [[ "$model_name" == *"Opus"* ]]; then
    model_short="Opus 4.5"
elif [[ "$model_name" == *"Sonnet"* ]]; then
    model_short="Sonnet 4.5"
fi

dir_name=$(basename "$current_dir")

branch=""
if git -C "$current_dir" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$current_dir" --no-optional-locks branch --show-current 2>/dev/null || echo "")
fi

# Format token displays
if [ "$used_tokens" -ge 1000 ]; then
    tokens_display="$((used_tokens / 1000))k"
else
    tokens_display="$used_tokens"
fi

if [ "$effective_context" -ge 1000 ]; then
    context_display="$((effective_context / 1000))k"
else
    context_display="$effective_context"
fi

# ANSI colors
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
TEAL='\033[36m'
RESET='\033[0m'

# Choose color based on percentage
if [ "$used_pct" -lt 30 ]; then
    COLOR="$GREEN"
elif [ "$used_pct" -lt 60 ]; then
    COLOR="$YELLOW"
else
    COLOR="$RED"
fi

# Build progress bar (10 units, each = 10%)
# Units 1-3: green, 4-6: yellow, 7-10: red
# Full units use =, partial unit uses ~
bar_width=10
filled=$((used_pct / 10))
if [ "$filled" -gt "$bar_width" ]; then
    filled=$bar_width
fi
partial=$((used_pct % 10))

bar="["
for ((i=1; i<=bar_width; i++)); do
    if [ "$i" -le 3 ]; then
        unit_color="$GREEN"
    elif [ "$i" -le 6 ]; then
        unit_color="$YELLOW"
    else
        unit_color="$RED"
    fi

    if [ "$i" -le "$filled" ]; then
        bar+="${unit_color}=${RESET}"
    elif [ "$i" -eq $((filled + 1)) ] && [ "$filled" -lt "$bar_width" ]; then
        bar+="${unit_color}~${RESET}"
    else
        bar+=" "
    fi
done
bar+="]"

output="$model_short | v$version | $bar ${COLOR}${used_pct}%${RESET} | ${tokens_display}/${context_display} | 📂 ${TEAL}${dir_name}${RESET}"

if [ -n "$branch" ]; then
    output="$output | 🌿 ${GREEN}${branch}${RESET}"
fi

if [ -n "$session_short" ]; then
    output="$output | ⚡ ${YELLOW}${session_short}${RESET}"
fi

echo -e "$output"
