#!/bin/bash

# Function to delete old files
delete_old_files() {
    local directory=$1
    local pattern=$2
    local age_minutes=$3

    echo "Searching for files matching the pattern $pattern in $directory that are older than $age_minutes minutes."

    # Find files matching the pattern
    local files=$(find "$directory" -name "$pattern" -type f)
    if [ -z "$files" ]; then
        echo "No files found with the specified pattern."
        return
    fi

    # Current date and time in seconds since the epoch
    local current_time=$(date +%s)

    # Process each file
    echo "Processing files..."
    echo "$files" | while read file; do
        echo "Checking file: $file"

        # Extract the timestamp from the filename
        local file_timestamp=$(echo "$file" | grep -oP '(?<=speedtest[-_])\d{14}' | head -n 1)
        if [ -z "$file_timestamp" ]; then
            echo "Skipping file (no timestamp found): $file"
            continue
        fi

        # Convert file timestamp to seconds since the epoch
        local file_time=$(date -d "${file_timestamp:0:4}-${file_timestamp:4:2}-${file_timestamp:6:2} ${file_timestamp:8:2}:${file_timestamp:10:2}:${file_timestamp:12:2}" +%s)

        # Calculate the age of the file in minutes
        local file_age=$(( (current_time - file_time) / 60 ))

        # Check if file is older than specified age
        if [ "$file_age" -gt "$age_minutes" ]; then
            echo "Deleting old file: $file (Age: $file_age minutes)"
            rm "$file"
        else
            echo "File is not old enough to delete: $file (Age: $file_age minutes)"
        fi
    done
}

# Main function
main() {
    # Directory where the files are located
    local directory="/usr/local/speedtest-monitor-results/static/images"

    # Pattern of the files to be deleted
    # Accounts for both underscore and hyphen variations
    local pattern="*speedtest[-_][0-9]{14}.png"

    # Age in minutes for file deletion (12 hours)
    local age_minutes=720

    delete_old_files "$directory" "$pattern" "$age_minutes"
}

# Execute main function
main
