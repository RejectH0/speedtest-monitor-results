#!/bin/bash
#
# This script is used to prune the files that are generated from the plots of each speedtest collector.
# Version 1.0 - 20240124-1930 GS
#
# Function to extract timestamp from file name
extract_timestamp() {
    local file=$1
    echo "$file" | grep -oP "(?<=speedtest[-_])\d{14}"
}

# Function to calculate file age in minutes
calculate_file_age() {
    local file_timestamp=$1
    local current_time=$(date +%s)
    local file_time=$(date -d "${file_timestamp:0:4}-${file_timestamp:4:2}-${file_timestamp:6:2} ${file_timestamp:8:2}:${file_timestamp:10:2}:${file_timestamp:12:2}" +%s)
    echo $(( (current_time - file_time) / 60 ))
}

# Function to delete file if older than specified age
delete_if_old() {
    local file=$1
    local file_age=$2
    local age_limit=$3

    if [ "$file_age" -gt "$age_limit" ]; then
        echo "Deleting old file: $file (Age: $file_age minutes)"
        rm "$file"
    else
        echo "File is not old enough to delete: $file (Age: $file_age minutes)"
    fi
}

# Main function
main() {
    local directory="/usr/local/speedtest-monitor-results/static/images"
    local pattern_underscore="*speedtest_??????????????.png"
    local pattern_hyphen="*speedtest-??????????????.png"
    local age_limit=720

    echo "Searching for files matching the patterns in $directory that are older than $age_limit minutes."

    for pattern in "$pattern_underscore" "$pattern_hyphen"; do
        find "$directory" -name "$pattern" -type f | while read file; do
            echo "Checking file: $file"
            local file_timestamp=$(extract_timestamp "$file")

            if [ -z "$file_timestamp" ]; then
                echo "Skipping file (no timestamp found): $file"
                continue
            fi

            local file_age=$(calculate_file_age "$file_timestamp")
            delete_if_old "$file" "$file_age" "$age_limit"
        done
    done
}

main
