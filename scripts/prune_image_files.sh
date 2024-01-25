#!/bin/bash

# Function to delete old files
delete_old_files() {
    local directory=$1
    local pattern=$2
    local age_minutes=$3

    echo "Searching for files matching the pattern $pattern in $directory that are older than $age_minutes minutes."

    # Find files matching the pattern and process each one
    find "$directory" -name "$pattern" -type f -exec bash -c '
        file="$0"
        age_minutes="$1"
        current_time=$(date +%s)

        echo "Checking file: $file"

        # Extract timestamp from filename
        file_timestamp=$(echo "$file" | grep -oP "(?<=speedtest[-_])\d{14}")
        if [ -z "$file_timestamp" ]; then
            echo "Skipping file (no timestamp found): $file"
            return
        fi

        # Convert file timestamp to seconds since the epoch
        file_time=$(date -d "${file_timestamp:0:4}-${file_timestamp:4:2}-${file_timestamp:6:2} ${file_timestamp:8:2}:${file_timestamp:10:2}:${file_timestamp:12:2}" +%s)

        # Calculate age of the file in minutes
        file_age=$(( (current_time - file_time) / 60 ))

        # Delete file if older than specified age
        if [ "$file_age" -gt "$age_minutes" ]; then
            echo "Deleting old file: $file (Age: $file_age minutes)"
            rm "$file"
        else
            echo "File is not old enough to delete: $file (Age: $file_age minutes)"
        fi
    ' {} "$age_minutes" \;
}

# Main function
main() {
    # Directory where the files are located
    local directory="/usr/local/speedtest-monitor-results/static/images"

    # Pattern of the files to be deleted
    local pattern="*speedtest[-_][0-9]{14}.png"

    # Age in minutes for file deletion (12 hours)
    local age_minutes=720

    delete_old_files "$directory" "$pattern" "$age_minutes"
}

# Execute main function
main
