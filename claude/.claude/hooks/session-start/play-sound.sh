#!/bin/bash

# Directory containing mp3 files
DIR="${1:-$HOME/Audio/claude/session-start}"

# Check if directory exists
if [ ! -d "$DIR" ]; then
    echo "Directory $DIR does not exist!"
    exit 1
fi

# Find all mp3 files in the directory
mapfile -t FILES < <(find "$DIR" -maxdepth 1 -type f -name "*.mp3")

# Check if any mp3 files were found
if [ ${#FILES[@]} -eq 0 ]; then
    echo "No files found in $DIR"
    exit 1
fi

# Select a random file
RANDOM_INDEX=$((RANDOM % ${#FILES[@]}))
RANDOM_FILE="${FILES[$RANDOM_INDEX]}"

# Play the file
echo "Playing: $(basename "$RANDOM_FILE")"
ffplay -v 0 -nodisp -autoexit "$RANDOM_FILE"
